# school/management/commands/import_thoikhoabieu.py
import json
from pathlib import Path
from typing import Dict, Tuple, List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from app.models import Thoikhoabieu 

REQUIRED_KEYS = {"lop", "thu", "buoi", "tiet", "mon"}

def _normalize_record(item: dict) -> dict:
    """
    Chuẩn hóa 1 dòng dữ liệu: strip khoảng trắng, ép kiểu, đồng nhất hoa/thường.
    Ném ValueError khi không hợp lệ.
    """
    missing = REQUIRED_KEYS - set(item.keys())
    if missing:
        raise ValueError(f"Thiếu keys: {', '.join(sorted(missing))}")

    lop = str(item["lop"]).strip().upper()
    buoi = str(item["buoi"]).strip().lower()
    mon = str(item["mon"]).strip()

    try:
        thu = int(item["thu"])
        tiet = int(item["tiet"])
    except (TypeError, ValueError):
        raise ValueError("`thu`/`tiet` phải là số nguyên")

    if not lop:
        raise ValueError("`lop` rỗng")
    if buoi not in {"sang", "chieu"}:
        raise ValueError("`buoi` chỉ nhận: sang, chieu")
    if not (2 <= thu <= 7):
        raise ValueError("`thu` nên trong khoảng 2..7")
    if tiet < 1:
        raise ValueError("`tiet` phải ≥ 1")
    if not mon:
        raise ValueError("`mon` rỗng")

    return {"lop": lop, "thu": thu, "buoi": buoi, "tiet": tiet, "mon": mon}


class Command(BaseCommand):
    help = "Import dữ liệu thời khóa biểu từ file JSON (danh sách object)."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Đường dẫn tới file thoikhoabieu.json (dạng list các object).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Chỉ kiểm tra/đếm, KHÔNG ghi vào DB.",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Nếu trùng (lop,thu,buoi,tiet) thì UPDATE `mon`. Mặc định là bỏ qua.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="XÓA toàn bộ bảng Thoikhoabieu trước khi import.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Batch size cho bulk_create/bulk_update (mặc định 1000).",
        )
        parser.add_argument(
            "--encoding",
            type=str,
            default="utf-8",
            help="Encoding file JSON (mặc định utf-8).",
        )
        parser.add_argument(
            "--fail-fast",
            action="store_true",
            help="Gặp lỗi dòng nào sẽ dừng ngay (mặc định: bỏ qua dòng lỗi và tiếp tục).",
        )

    def handle(self, *args, **opts):
        path = Path(opts["json_file"])
        if not path.exists():
            raise CommandError(f"Không tìm thấy file: {path}")

        try:
            with path.open("r", encoding=opts["encoding"]) as f:
                raw = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f"File JSON không hợp lệ: {e}") from e
        except Exception as e:
            raise CommandError(f"Lỗi khi đọc file: {e}") from e

        if not isinstance(raw, list):
            raise CommandError("JSON phải là một LIST các object.")

        normalized: Dict[Tuple[str, int, str, int], dict] = {}
        invalid_rows: List[str] = []

        for idx, item in enumerate(raw, start=1):
            try:
                rec = _normalize_record(item)
                key = (rec["lop"], rec["thu"], rec["buoi"], rec["tiet"])
                normalized[key] = rec
            except Exception as e:
                msg = f"Dòng {idx}: {e}"
                if opts["fail-fast"]:
                    raise CommandError(msg)
                invalid_rows.append(msg)

        total_in_file = len(raw)
        unique_in_file = len(normalized)

        keys = list(normalized.keys())
        lops = {k[0] for k in keys}

        existing_qs = Thoikhoabieu.objects.filter(lop__in=lops)
        existing_map: Dict[Tuple[str, int, str, int], Thoikhoabieu] = {}
        for row in existing_qs.only("id", "lop", "thu", "buoi", "tiet", "mon"):
            key = (row.lop, row.thu, row.buoi, row.tiet)
            existing_map[key] = row

        to_create: List[Thoikhoabieu] = []
        to_update: List[Thoikhoabieu] = []
        skipped = 0

        for key, rec in normalized.items():
            exist = existing_map.get(key)
            if exist:
                if opts["update"]:
                    if exist.mon != rec["mon"]:
                        exist.mon = rec["mon"]
                        to_update.append(exist)
                    else:
                        skipped += 1
                else:
                    skipped += 1
            else:
                to_create.append(Thoikhoabieu(**rec))

        summary = {
            "total_rows_in_file": total_in_file,
            "unique_rows_in_file": unique_in_file,
            "invalid_rows": len(invalid_rows),
            "will_create": len(to_create),
            "will_update": len(to_update),
            "will_skip": skipped,
            "clear_before_import": bool(opts["clear"]),
            "dry_run": bool(opts["dry_run"]),
            "update_mode": bool(opts["update"]),
        }

        if invalid_rows:
            self.stdout.write(self.style.WARNING("Một số dòng không hợp lệ:"))
            for msg in invalid_rows[:20]:
                self.stdout.write(self.style.WARNING(f"  - {msg}"))
            if len(invalid_rows) > 20:
                self.stdout.write(self.style.WARNING(f"  ... và {len(invalid_rows)-20} dòng nữa"))

        self.stdout.write(self.style.NOTICE("TÓM TẮT DỰ KIẾN:"))
        for k, v in summary.items():
            self.stdout.write(f"  {k}: {v}")

        if opts["dry_run"]:
            self.stdout.write(self.style.SUCCESS("Dry-run xong. Không ghi vào DB."))
            return

        with transaction.atomic():
            if opts["clear"]:
                Thoikhoabieu.objects.all().delete()

            if to_create:
                Thoikhoabieu.objects.bulk_create(
                    to_create, batch_size=opts["batch_size"]
                )

            if to_update:
                Thoikhoabieu.objects.bulk_update(
                    to_update, fields=["mon"], batch_size=opts["batch_size"]
                )

        self.stdout.write(self.style.SUCCESS(
            f"Import xong. Tạo mới: {len(to_create)}, cập nhật: {len(to_update)}, bỏ qua: {skipped}, lỗi: {len(invalid_rows)}"
        ))
