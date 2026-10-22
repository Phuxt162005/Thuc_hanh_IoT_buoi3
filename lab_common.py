"""Các tiện ích nhỏ dùng chung cho ba bài."""

import argparse
import asyncio
import csv
import json
import math
import re
from datetime import datetime
from pathlib import Path

import aiocoap


def timestamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def positive_number(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Phai la so duong huu han")
    return number


def device_ids(value):
    devices = [item.strip() for item in value.split(",")]
    if any(not re.fullmatch(r"[a-zA-Z0-9_-]+", item) for item in devices):
        raise argparse.ArgumentTypeError("Ma thiet bi chi gom chu, so, _ va -")
    if len(set(devices)) != len(devices):
        raise argparse.ArgumentTypeError("Ma thiet bi khong duoc trung")
    return devices


def single_device(value):
    devices = device_ids(value)
    if len(devices) != 1:
        raise argparse.ArgumentTypeError("Chon mot thiet bi")
    return devices[0]


def parser(description, *, server=False):
    result = argparse.ArgumentParser(description=description)
    result.add_argument("--host", default="127.0.0.1")
    result.add_argument("--port", type=int, default=5683)
    if not server:
        result.add_argument("--timeout", type=positive_number, default=5,
                            help="Gioi han cho moi request, mac dinh 5 giay")
        result.add_argument("--non", action="store_true", help="Gui NON thay vi CON")
    return result


def uri(args, path):
    host = f"[{args.host}]" if ":" in args.host and not args.host.startswith("[") else args.host
    return f"coap://{host}:{args.port}/{path.lstrip('/')}"


def message(args, code, path, *, payload=b"", content_format=None, observe=False):
    request = aiocoap.Message(code=code, uri=uri(args, path), payload=payload,
                             transport_tuning=aiocoap.Unreliable if args.non else aiocoap.Reliable)
    if content_format is not None:
        request.opt.content_format = content_format
    if observe:
        request.opt.observe = 0
    return request


async def exchange(context, request, timeout):
    """Timeout hủy response future để thư viện dừng request/retry."""
    pending = context.request(request)
    try:
        return await asyncio.wait_for(pending.response, timeout)
    except BaseException:
        if pending.observation is not None and not pending.observation.cancelled:
            pending.observation.cancel()
        raise


async def keyboard(prompt):
    try:
        return (await asyncio.to_thread(input, prompt)).strip()
    except EOFError:
        return None


def show_response(response):
    print("Code:", response.code)
    print("Payload:", response.payload.decode("utf-8", errors="replace"))


def error_response(text):
    return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=text.encode("utf-8"), content_format=0)


def json_response(data):
    return aiocoap.Message(code=aiocoap.CONTENT,
                          payload=json.dumps(data, ensure_ascii=False).encode("utf-8"), content_format=50)


class Recorder:
    """CSV hoặc JSON array; giữ lịch sử khi mở lại, không ghi đè file cũ."""

    def __init__(self, filename, fields):
        self.path = Path(filename) if filename else None
        self.fields = fields
        if self.path:
            if self.path.suffix.lower() not in (".csv", ".json"):
                raise ValueError("File ket qua phai co duoi .csv hoac .json")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                if self.path.suffix.lower() == ".json":
                    data = self._read_json()
                    if not isinstance(data, list) or any(not isinstance(row, dict) or set(row) != set(fields) for row in data):
                        raise ValueError("File JSON cu khong dung schema; hay chon file moi")
                else:
                    with self.path.open(encoding="utf-8", newline="") as stream:
                        if next(csv.reader(stream), None) != fields:
                            raise ValueError("Header CSV cu khong khop; hay chon file moi")

    def _read_json(self):
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError(f"File JSON khong hop le: {self.path} ({error})") from error

    def write(self, row):
        if not self.path:
            return
        if self.path.suffix.lower() == ".csv":
            has_header = self.path.exists() and self.path.stat().st_size > 0
            with self.path.open("a", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=self.fields)
                if not has_header:
                    writer.writeheader()
                writer.writerow(row)
        else:
            data = self._read_json() if self.path.exists() else []
            data.append(row)
            temporary = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(self.path)


def run(main, args):
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\nDa dung chuong trinh.")
    except (OSError, ValueError) as error:
        print("Khong the chay:", error)
        raise SystemExit(1) from None
