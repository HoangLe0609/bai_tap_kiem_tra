from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


# ==========================================
# 1. KHỞI TẠO ỨNG DỤNG VÀ DATABASE
# ==========================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-chi-dung-khi-phat-trien"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsach.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==========================================
# 2. KHAI BÁO MODEL
# ==========================================

class DanhMucSach(db.Model):
    __tablename__ = "danh_muc_sach"

    id: Mapped[int] = mapped_column(primary_key=True)
    ten_danh_muc: Mapped[str] = mapped_column(String(100), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Một danh mục có nhiều sách
    sach: Mapped[list["Sach"]] = relationship(
        back_populates="danh_muc"
    )

    def __repr__(self):
        return f"<DanhMucSach {self.ten_danh_muc}>"


class Sach(db.Model):
    __tablename__ = "sach"

    id: Mapped[int] = mapped_column(primary_key=True)
    ten_sach: Mapped[str] = mapped_column(String(200), nullable=False)
    tac_gia: Mapped[str] = mapped_column(String(100), nullable=False)
    nam_xuat_ban: Mapped[int] = mapped_column(Integer, nullable=False)
    gia_ban: Mapped[float] = mapped_column(Float, nullable=False)
    so_luong: Mapped[int] = mapped_column(Integer, nullable=False)

    # Khóa ngoại đến bảng DanhMucSach
    danh_muc_id: Mapped[int] = mapped_column(
        ForeignKey("danh_muc_sach.id"),
        nullable=False
    )

    # Mỗi sách thuộc một danh mục
    danh_muc: Mapped["DanhMucSach"] = relationship(
        back_populates="sach"
    )

    def __repr__(self):
        return f"<Sach {self.ten_sach}>"


# ==========================================
# TẠO DATABASE VÀ THÊM DỮ LIỆU MẪU
# ==========================================

with app.app_context():

    db.create_all()

    # Chỉ thêm dữ liệu mẫu khi CSDL chưa có dữ liệu
    so_danh_muc = db.session.scalar(
        db.select(func.count(DanhMucSach.id))
    ) or 0

    so_sach = db.session.scalar(
        db.select(func.count(Sach.id))
    ) or 0

    if so_danh_muc == 0 and so_sach == 0:

        # ----------------------------------
        # Thêm danh mục mẫu
        # ----------------------------------

        dm1 = DanhMucSach(
            ten_danh_muc="Công nghệ thông tin",
            mo_ta="Sách về lập trình và công nghệ"
        )

        dm2 = DanhMucSach(
            ten_danh_muc="Kinh tế",
            mo_ta="Sách về kinh tế và quản trị"
        )

        dm3 = DanhMucSach(
            ten_danh_muc="Văn học",
            mo_ta="Sách văn học Việt Nam và thế giới"
        )

        dm4 = DanhMucSach(
            ten_danh_muc="Khoa học",
            mo_ta="Sách về khoa học và kỹ thuật"
        )

        db.session.add_all([dm1, dm2, dm3, dm4])

        # Lưu danh mục để có ID
        db.session.flush()

        # ----------------------------------
        # Thêm sách mẫu
        # ----------------------------------

        sachs = [
            Sach(
                ten_sach="Python cơ bản",
                tac_gia="Nguyễn Văn A",
                nam_xuat_ban=2023,
                gia_ban=120000,
                so_luong=20,
                danh_muc=dm1
            ),

            Sach(
                ten_sach="Lập trình Web với Flask",
                tac_gia="Trần Văn B",
                nam_xuat_ban=2024,
                gia_ban=150000,
                so_luong=15,
                danh_muc=dm1
            ),

            Sach(
                ten_sach="Cơ sở dữ liệu",
                tac_gia="Lê Văn C",
                nam_xuat_ban=2022,
                gia_ban=135000,
                so_luong=12,
                danh_muc=dm1
            ),

            Sach(
                ten_sach="Kinh tế học đại cương",
                tac_gia="Phạm Văn D",
                nam_xuat_ban=2021,
                gia_ban=180000,
                so_luong=10,
                danh_muc=dm2
            ),

            Sach(
                ten_sach="Quản trị kinh doanh",
                tac_gia="Hoàng Văn E",
                nam_xuat_ban=2023,
                gia_ban=200000,
                so_luong=8,
                danh_muc=dm2
            ),

            Sach(
                ten_sach="Truyện Kiều",
                tac_gia="Nguyễn Du",
                nam_xuat_ban=2020,
                gia_ban=85000,
                so_luong=25,
                danh_muc=dm3
            ),

            Sach(
                ten_sach="Dế Mèn phiêu lưu ký",
                tac_gia="Tô Hoài",
                nam_xuat_ban=2022,
                gia_ban=95000,
                so_luong=18,
                danh_muc=dm3
            ),

            Sach(
                ten_sach="Vũ trụ trong vỏ hạt dẻ",
                tac_gia="Stephen Hawking",
                nam_xuat_ban=2021,
                gia_ban=160000,
                so_luong=7,
                danh_muc=dm4
            )
        ]

        db.session.add_all(sachs)
        db.session.commit()

        print("Đã thêm dữ liệu mẫu thành công!")


# ==========================================
# 3. DASHBOARD
# ==========================================

@app.get("/")
@app.get("/dashboard")
def dashboard():

    # Tổng số danh mục
    so_danh_muc = db.session.scalar(
        db.select(func.count(DanhMucSach.id))
    ) or 0

    # Tổng số đầu sách
    so_dau_sach = db.session.scalar(
        db.select(func.count(Sach.id))
    ) or 0

    # Tổng số lượng sách
    tong_so_luong = db.session.scalar(
        db.select(func.sum(Sach.so_luong))
    ) or 0

    # Thống kê số đầu sách theo danh mục
    ket_qua = db.session.execute(
        db.select(
            DanhMucSach.ten_danh_muc,
            func.count(Sach.id).label("so_dau_sach")
        )
        .outerjoin(Sach)
        .group_by(DanhMucSach.id, DanhMucSach.ten_danh_muc)
        .order_by(DanhMucSach.ten_danh_muc)
    ).all()

    thong_ke_danh_muc = [
        {
            "ten_danh_muc": row.ten_danh_muc,
            "so_dau_sach": row.so_dau_sach
        }
        for row in ket_qua
    ]

    # 5 sách được thêm gần đây nhất
    sach_moi = db.session.execute(
        db.select(Sach)
        .order_by(Sach.id.desc())
        .limit(5)
    ).scalars().all()

    return render_template(
        "dashboard.html",
        so_danh_muc=so_danh_muc,
        so_dau_sach=so_dau_sach,
        tong_so_luong=tong_so_luong,
        thong_ke_danh_muc=thong_ke_danh_muc,
        sach_moi=sach_moi
    )


# ==========================================
# 4. CRUD DANH MỤC SÁCH
# ==========================================

# Hiển thị danh sách danh mục
@app.get("/danh-muc")
def danh_muc_list():

    danh_mucs = db.session.execute(
        db.select(DanhMucSach)
        .order_by(DanhMucSach.id.desc())
    ).scalars().all()

    return render_template(
        "danhmuc.html",
        danh_mucs=danh_mucs
    )


# Thêm danh mục
@app.route("/danh-muc/them", methods=["GET", "POST"])
def them_danh_muc():

    if request.method == "POST":

        ten = request.form.get("ten_danh_muc", "").strip()
        mo_ta = request.form.get("mo_ta", "").strip()

        if not ten:
            flash("Vui lòng nhập tên danh mục!", "danger")
            return redirect(url_for("them_danh_muc"))

        if len(ten) > 100:
            flash("Tên danh mục không được vượt quá 100 ký tự!", "danger")
            return redirect(url_for("them_danh_muc"))

        danh_muc = DanhMucSach(
            ten_danh_muc=ten,
            mo_ta=mo_ta or None
        )

        db.session.add(danh_muc)
        db.session.commit()

        flash("Thêm danh mục thành công!", "success")
        return redirect(url_for("danh_muc_list"))

    return render_template("them_danhmuc.html")


# Sửa danh mục
@app.route("/danh-muc/sua/<int:id>", methods=["GET", "POST"])
def sua_danh_muc(id):

    danh_muc = db.session.get(DanhMucSach, id)

    if danh_muc is None:
        flash("Không tìm thấy danh mục!", "danger")
        return redirect(url_for("danh_muc_list"))

    if request.method == "POST":

        ten = request.form.get("ten_danh_muc", "").strip()
        mo_ta = request.form.get("mo_ta", "").strip()

        if not ten:
            flash("Vui lòng nhập tên danh mục!", "danger")
            return redirect(url_for("sua_danh_muc", id=id))

        if len(ten) > 100:
            flash("Tên danh mục không được vượt quá 100 ký tự!", "danger")
            return redirect(url_for("sua_danh_muc", id=id))

        danh_muc.ten_danh_muc = ten
        danh_muc.mo_ta = mo_ta or None

        db.session.commit()

        flash("Cập nhật danh mục thành công!", "success")
        return redirect(url_for("danh_muc_list"))

    return render_template(
        "sua_danhmuc.html",
        danh_muc=danh_muc
    )


# Xóa danh mục
@app.post("/danh-muc/xoa/<int:id>")
def xoa_danh_muc(id):

    danh_muc = db.session.get(DanhMucSach, id)

    if danh_muc is None:
        flash("Không tìm thấy danh mục!", "danger")
        return redirect(url_for("danh_muc_list"))

    # Không cho xóa danh mục nếu còn sách
    if danh_muc.sach:
        flash(
            "Không thể xóa danh mục đang chứa sách!",
            "danger"
        )
        return redirect(url_for("danh_muc_list"))

    db.session.delete(danh_muc)
    db.session.commit()

    flash("Xóa danh mục thành công!", "success")
    return redirect(url_for("danh_muc_list"))


# ==========================================
# 5. HÀM LẤY VÀ KIỂM TRA DỮ LIỆU SÁCH
# ==========================================

def lay_du_lieu_sach():

    ten_sach = request.form.get("ten_sach", "").strip()
    tac_gia = request.form.get("tac_gia", "").strip()

    if not ten_sach:
        raise ValueError("Vui lòng nhập tên sách!")

    if not tac_gia:
        raise ValueError("Vui lòng nhập tên tác giả!")

    if len(ten_sach) > 200:
        raise ValueError("Tên sách không được vượt quá 200 ký tự!")

    if len(tac_gia) > 100:
        raise ValueError("Tên tác giả không được vượt quá 100 ký tự!")

    try:
        nam_xuat_ban = int(request.form.get("nam_xuat_ban", ""))
    except ValueError:
        raise ValueError("Năm xuất bản phải là số nguyên!")

    try:
        gia_ban = float(request.form.get("gia_ban", ""))
    except ValueError:
        raise ValueError("Giá bán phải là số!")

    try:
        so_luong = int(request.form.get("so_luong", ""))
    except ValueError:
        raise ValueError("Số lượng phải là số nguyên!")

    try:
        danh_muc_id = int(request.form.get("danh_muc_id", ""))
    except ValueError:
        raise ValueError("Vui lòng chọn danh mục sách!")

    if nam_xuat_ban <= 0:
        raise ValueError("Năm xuất bản phải lớn hơn 0!")

    if gia_ban < 0:
        raise ValueError("Giá bán không được âm!")

    if so_luong < 0:
        raise ValueError("Số lượng không được âm!")

    danh_muc = db.session.get(DanhMucSach, danh_muc_id)

    if danh_muc is None:
        raise ValueError("Danh mục sách không tồn tại!")

    return {
        "ten_sach": ten_sach,
        "tac_gia": tac_gia,
        "nam_xuat_ban": nam_xuat_ban,
        "gia_ban": gia_ban,
        "so_luong": so_luong,
        "danh_muc_id": danh_muc_id
    }


# ==========================================
# 6. CRUD SÁCH
# ==========================================

# Hiển thị danh sách sách
@app.get("/sach")
def sach_list():

    # Lấy danh sách danh mục
    danh_mucs = db.session.execute(
        db.select(DanhMucSach)
        .order_by(DanhMucSach.ten_danh_muc)
    ).scalars().all()

    # Lấy ID danh mục được chọn từ URL
    danh_muc_id = request.args.get("danh_muc_id", type=int)

    # Tạo câu truy vấn sách
    stmt = db.select(Sach).order_by(Sach.id.desc())

    # Nếu có chọn danh mục thì lọc sách theo danh mục
    if danh_muc_id is not None:
        stmt = stmt.where(Sach.danh_muc_id == danh_muc_id)

    sachs = db.session.execute(stmt).scalars().all()

    return render_template(
        "sach.html",
        sachs=sachs,
        danh_mucs=danh_mucs,
        danh_muc_id=danh_muc_id
    )


# Thêm sách
@app.route("/sach/them", methods=["GET", "POST"])
def them_sach():

    danh_mucs = db.session.execute(
        db.select(DanhMucSach)
        .order_by(DanhMucSach.ten_danh_muc)
    ).scalars().all()

    if request.method == "POST":

        try:
            du_lieu = lay_du_lieu_sach()

            sach = Sach(**du_lieu)

            db.session.add(sach)
            db.session.commit()

            flash("Thêm sách thành công!", "success")
            return redirect(url_for("sach_list"))

        except ValueError as e:
            flash(str(e), "danger")

        except Exception:
            db.session.rollback()
            flash("Có lỗi xảy ra khi thêm sách!", "danger")

    return render_template(
        "them_sach.html",
        danh_mucs=danh_mucs
    )


# Sửa sách
@app.route("/sach/sua/<int:id>", methods=["GET", "POST"])
def sua_sach(id):

    sach = db.session.get(Sach, id)

    if sach is None:
        flash("Không tìm thấy sách!", "danger")
        return redirect(url_for("sach_list"))

    danh_mucs = db.session.execute(
        db.select(DanhMucSach)
        .order_by(DanhMucSach.ten_danh_muc)
    ).scalars().all()

    if request.method == "POST":

        try:
            du_lieu = lay_du_lieu_sach()

            sach.ten_sach = du_lieu["ten_sach"]
            sach.tac_gia = du_lieu["tac_gia"]
            sach.nam_xuat_ban = du_lieu["nam_xuat_ban"]
            sach.gia_ban = du_lieu["gia_ban"]
            sach.so_luong = du_lieu["so_luong"]
            sach.danh_muc_id = du_lieu["danh_muc_id"]

            db.session.commit()

            flash("Cập nhật sách thành công!", "success")
            return redirect(url_for("sach_list"))

        except ValueError as e:
            flash(str(e), "danger")

        except Exception:
            db.session.rollback()
            flash("Có lỗi xảy ra khi cập nhật sách!", "danger")

    return render_template(
        "sua_sach.html",
        sach=sach,
        danh_mucs=danh_mucs
    )


# Xóa sách
@app.post("/sach/xoa/<int:id>")
def xoa_sach(id):

    sach = db.session.get(Sach, id)

    if sach is None:
        flash("Không tìm thấy sách!", "danger")
        return redirect(url_for("sach_list"))

    db.session.delete(sach)
    db.session.commit()

    flash("Xóa sách thành công!", "success")
    return redirect(url_for("sach_list"))


# ==========================================
# 7. CHẠY ỨNG DỤNG
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)