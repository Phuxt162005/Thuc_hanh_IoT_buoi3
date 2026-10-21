# THỰC HÀNH PYTHON VỚI GIAO THỨC CoAP

## 1. Thông tin sinh viên

- Họ và tên: Bùi Hồng Phú
- Mã sinh viên: B23DCCN651

## 2. Giới thiệu

Bài thực hành gồm ba nội dung nhằm làm quen với giao tiếp IoT sử dụng giao thức CoAP:

1. Gửi và nhận thông điệp cơ bản bằng GET và POST.
2. Mô phỏng cảm biến nhiệt độ, độ ẩm và giám sát dữ liệu bằng GET định kỳ.
3. Giám sát, điều khiển đèn thông minh bằng GET, PUT và CoAP Observe.

## 3. Môi trường sử dụng

- Hệ điều hành: Windows
- Python: 3.14
- Thư viện: `aiocoap 0.4.17`
- Giao thức: CoAP qua UDP
- Địa chỉ thử nghiệm: `127.0.0.1`
- Cổng CoAP: `5683`

Không cần cài đặt RabbitMQ, MQTT Broker hoặc dịch vụ trung gian khác.

### Cài đặt thư viện

Mở terminal tại thư mục dự án và chạy:

```powershell
python -m pip install aiocoap
```

Kiểm tra phiên bản thư viện:

```powershell
python -m pip show aiocoap
```

### Lưu ý về địa chỉ và cổng

Các Server trong bài được cấu hình lắng nghe tại `127.0.0.1:5683`. Vì vậy, các Client sử dụng `127.0.0.1`, không dùng `localhost`.

Các bài đều dùng cổng UDP `5683`; chỉ chạy một CoAP Server tại một thời điểm. Trước khi chuyển bài, nhấn `Ctrl+C` để dừng Server đang chạy.

## 4. Cấu trúc thư mục

```text
CoAP_Lab/
├── bai1/
│   ├── coap_server_bai1.py
│   └── coap_client_bai1.py
├── bai2/
│   ├── sensor_server_bai2.py
│   └── monitor_client_bai2.py
├── bai3/
│   ├── light_server_bai3.py
│   ├── light_controller_bai3.py
│   └── light_monitor_bai3.py
├── evidence/
│   ├── bai1_client.png
│   ├── bai1_server.png
│   ├── bai2_client.png
│   ├── bai2_server.png
│   ├── bai3_controller.png
│   ├── bai3_monitor.png
│   └── bai3_server.png
└── README.md
```

Thư mục `evidence/` dùng để lưu ảnh chụp kết quả chạy thực tế. Thêm các ảnh terminal đã chụp vào thư mục này trước khi nộp để làm minh chứng trực quan.

## 5. Địa chỉ tài nguyên CoAP

| Bài | URI | Phương thức | Mục đích |
|---|---|---|---|
| Bài 1 | `coap://127.0.0.1:5683/iot/lab/message` | GET, POST | Nhận lời chào từ Server và gửi thông điệp sinh viên |
| Bài 2 | `coap://127.0.0.1:5683/iot/lab/sensor01/data` | GET | Truy vấn dữ liệu nhiệt độ và độ ẩm |
| Bài 3 | `coap://127.0.0.1:5683/iot/lab/light01/status` | GET, PUT, Observe | Đọc trạng thái, điều khiển đèn và nhận thông báo thay đổi |

## 6. Cách chạy từng bài

Mở terminal tại thư mục gốc `CoAP_Lab`. Mỗi chương trình chạy trong một terminal riêng khi cần đồng thời Server và Client.

### Bài 1 — Gửi và nhận thông điệp cơ bản

**Terminal 1 — Server:**

```powershell
python bai1/coap_server_bai1.py
```

**Terminal 2 — Client:**

```powershell
python bai1/coap_client_bai1.py
```

Client gửi GET để nhận lời chào từ Server, sau đó yêu cầu nhập họ tên và mã sinh viên rồi gửi POST. Server in payload cùng thời điểm nhận và trả lời xác nhận.

Mã phản hồi mong đợi:

- GET: `2.05 Content`
- POST: `2.04 Changed`

Ví dụ đầu ra Client:

```text
Sending GET request...
URI: coap://127.0.0.1:5683/iot/lab/message

Response:
Code: 2.05 Content
Payload: Xin chao tu CoAP Server

Sending POST request...
Payload: Xin chao tu CoAP Client - B23DCCN651 - Bui Hong Phu

Response:
Code: 2.04 Changed
Payload: Server da nhan thong diep
```

### Bài 2 — Mô phỏng cảm biến nhiệt độ và độ ẩm

**Terminal 1 — Sensor Server:**

```powershell
python bai2/sensor_server_bai2.py
```

**Terminal 2 — Monitoring Client:**

```powershell
python bai2/monitor_client_bai2.py
```

Server sinh dữ liệu ngẫu nhiên và cập nhật sau mỗi 3 giây. Client gửi GET định kỳ mỗi 3 giây, phân tích JSON và hiển thị mã thiết bị, nhiệt độ, độ ẩm và thời điểm nhận.

Điều kiện cảnh báo:

- Nhiệt độ `> 35°C`: `CANH BAO: Nhiet do cao`.
- Độ ẩm `< 40%`: `CANH BAO: Do am thap`.
- Nếu không có điều kiện nào được thỏa mãn, Client hiển thị trạng thái bình thường.

Ví dụ đầu ra:

```text
[12:03:44] Received sensor data
Device: sensor01
Temperature: 39.2 C
Humidity: 61.9 %
CANH BAO: Nhiet do cao
------------------------------
```

Dữ liệu ở mỗi lần nhận thay đổi vì Server sinh số đo ngẫu nhiên.

### Bài 3 — Điều khiển đèn thông minh bằng CoAP Observe

Bắt đầu bằng trạng thái đèn `OFF`. Mở ba terminal riêng và chạy theo thứ tự sau.

**Terminal 1 — Smart Light Server:**

```powershell
python bai3/light_server_bai3.py
```

**Terminal 2 — Monitoring Client:**

```powershell
python bai3/light_monitor_bai3.py
```

Chờ đến khi thấy `Observe registration successful` và trạng thái ban đầu của `light01`. Để Client tiếp tục chạy.

**Terminal 3 — Controller Client:**

```powershell
python bai3/light_controller_bai3.py
```

Nhập các lệnh để kiểm thử:

- `ON`: gửi PUT để bật đèn.
- `STATUS`: gửi GET để xem trạng thái hiện tại.
- `OFF`: gửi PUT để tắt đèn.
- `EXIT`: kết thúc Controller.

Monitoring Client phải tự nhận thông báo `State Updated` khi trạng thái chuyển từ `OFF` sang `ON` và từ `ON` sang `OFF`. Client sử dụng Observe, không gửi GET polling định kỳ.

Mã phản hồi mong đợi:

- GET trạng thái: `2.05 Content`.
- PUT điều khiển: `2.04 Changed`.

## 7. Kết quả kiểm thử

Các chương trình đã được chạy trên máy local; kết quả đối chiếu theo terminal như sau.

### Bài 1

- Server khởi động tại cổng 5683 và cung cấp tài nguyên `/iot/lab/message`.
- Client nhận được `2.05 Content` với payload `Xin chao tu CoAP Server`.
- Client gửi POST chứa thông tin sinh viên và nhận `2.04 Changed` với payload `Server da nhan thong diep`.
- Server hiển thị payload POST và thời điểm nhận.

### Bài 2

- Server cập nhật và in dữ liệu cảm biến mới mỗi 3 giây.
- Client nhận dữ liệu JSON qua GET, hiển thị thời điểm nhận, mã thiết bị, nhiệt độ và độ ẩm.
- Các trường hợp đã quan sát được cảnh báo nhiệt độ cao khi nhiệt độ lớn hơn 35°C và cảnh báo độ ẩm thấp khi độ ẩm nhỏ hơn 40%.

### Bài 3

- Server khởi động với trạng thái ban đầu `OFF`.
- Controller nhận `2.04 Changed` khi gửi `ON` và `OFF`, đồng thời GET `STATUS` trả `2.05 Content` và trạng thái JSON phù hợp.
- Monitoring Client đăng ký Observe thành công, nhận trạng thái ban đầu `OFF`, rồi nhận thông báo tự động khi đèn chuyển sang `ON` và trở về `OFF`.
- Kết quả kiểm thử xác nhận Monitoring Client nhận notification qua CoAP Observe, không dùng GET polling định kỳ.

## 8. Dừng chương trình

- Nhấn `Ctrl+C` ở terminal Server để dừng Server.
- Nhấn `Ctrl+C` ở Monitoring Client để dừng theo dõi Observe hoặc giám sát cảm biến.
- Ở Light Controller Client, nhập `EXIT` để kết thúc chương trình.

## 9. Tài liệu tham khảo

- Tài liệu buổi thực hành: *Lập trình Python với giao thức CoAP*.
- Tài liệu thư viện aiocoap: <https://aiocoap.readthedocs.io/>.
