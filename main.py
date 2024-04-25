from fastapi import FastAPI, Response, HTTPException  # mengimpor kelas FastAPI dari modul fastapi 
from typing import Optional  # mengimpor tipe Optional dari modul typing 
from pydantic import BaseModel  # mengimpor BaseModel dari modul pydantic
from fastapi import File, UploadFile  # mengimpor kelas File dan UploadFile dari modul fastapi
from fastapi.responses import FileResponse  # mengimpor kelas FileResponse dari modul fastapi.responses
import sqlite3  # mengimpor modul sqlite3 

class Mhs(BaseModel): # membuat class Mhs sebagai turunan dari BaseModel 
    nim: str  # nim mahasiswa (string)
    nama: str  # nama mahasiswa (string)
    id_prov: str  # id provinsi mahasiswa (string)
    angkatan: str  # tahun angkatan mahasiswa (string)
    tinggi_badan: int | None = None  # tinggi badan mahasiswa (integer) atau None jika tidak ada data

class MhsPatch(BaseModel):  # membuat kelas model MhsPatch 
    # nama mahasiswa (string), default None jika tidak disediakan
    nama: Optional[str] = "kosong"
    # id provinsi mahasiswa (string), default None jika tidak disediakan
    id_prov: Optional[str] = "kosong"
    # tahun angkatan mahasiswa (string), default None jika tidak disediakan
    angkatan: Optional[str] = "kosong"
    # tinggi badan mahasiswa (integer), default -9999 jika tidak disediakan
    tinggi_badan: Optional[int] = -9999

app = FastAPI()  # membuat instance aplikasi FastAPI

@app.get("/daftar_mhs/")  # mendefinisikan route HTTP GET /daftar_mhs/
def daftar_mhs(id_prov: str, angkatan: str):  # menyediakan fungsi untuk route /daftar_mhs/ dengan parameter id_prov dan angkatan
    return {  # mengembalikan respons 
        "query": " idprov: {} ; angkatan: {}".format(id_prov, angkatan),  # mengisi data query dengan id_prov dan angkatan
        "data": [{"nim": "1234"}, {"nim": "1235"}]  # data mahasiswa (misalnya NIM) yang dikirimkan dalam respons
    }

@app.post("/tambah_mhs/")  # mendefinisikan route HTTP POST /tambah_mhs/ untuk menambahkan data mahasiswa
def tambah_mhs(m: Mhs):  # menggunakan model Mhs sebagai parameter untuk validasi data masukan
    try:
        # nama database 
        DB_NAME = "upi.db"
        # membuat koneksi ke database 
        con = sqlite3.connect(DB_NAME)
        # membuat objek cursor untuk eksekusi perintah sql
        cur = con.cursor()

        # query untuk menambahkan data mahasiswa ke tabel 'mahasiswa'
        query = """INSERT INTO mahasiswa (nim, nama, id_prov, angkatan, tinggi_badan)
                   VALUES (?, ?, ?, ?, ?)"""
        # menjalankan query dengan menggunakan parameterized query untuk menghindari sql injection
        cur.execute(query, (m.nim, m.nama, m.id_prov, m.angkatan, m.tinggi_badan))
        # commit perubahan ke database
        con.commit()

    except Exception as e:
        # mengembalikan pesan error jika terjadi kesalahan
        return ({"status": f"terjadi error: {e}"})

    finally:
        # menutup koneksi ke database setelah selesai
        con.close()

    # mengembalikan pesan berhasil jika semua langkah selesai tanpa masalah
    return {"status": "ok berhasil insert satu record"}

@app.get("/tampilkan_semua_mhs/")
def tampil_semua_mhs():
    try:
        # nama database 
        DB_NAME = "upi.db"
        # membuat koneksi ke database 
        con = sqlite3.connect(DB_NAME)
        # membuat objek cursor untuk eksekusi perintah sql
        cur = con.cursor()
        
        # inisialisasi list untuk menyimpan data mahasiswa
        recs = []
        # mengambil semua baris (record) dari tabel 'mahasiswa' dan memasukkannya ke dalam list recs
        for row in cur.execute("SELECT * FROM mahasiswa"):
            recs.append(row)
    
    except Exception as e:
        # mengembalikan pesan error jika terjadi kesalahan
        return ({"status": f"terjadi error: {e}"})
    
    finally:
        # menutup koneksi ke database setelah selesai
        con.close()
    
    # mengembalikan data mahasiswa jika berhasil
    return {"data": recs}

@app.put("/update_mhs_put/{nim}", response_model=Mhs)  # mendefinisikan route HTTP PUT /update_mhs_put/{nim} untuk memperbarui data mahasiswa
def update_mhs_put(nim: str, m: Mhs, response: Response):
    try:
        # nama database 
        DB_NAME = "upi.db"
        # membuat koneksi ke database 
        con = sqlite3.connect(DB_NAME)
        # membuat objek cursor untuk eksekusi perintah sql
        cur = con.cursor()

        # memeriksa apakah data mahasiswa dengan nim tertentu ada dalam database
        cur.execute("SELECT * FROM mahasiswa WHERE nim = ?", (nim,))
        existing_item = cur.fetchone()

        # jika data mahasiswa ditemukan, lakukan update
        if existing_item:
            cur.execute("UPDATE mahasiswa SET nama = ?, id_prov = ?, angkatan = ?, tinggi_badan = ? WHERE nim = ?", 
                        (m.nama, m.id_prov, m.angkatan, m.tinggi_badan, nim))
            con.commit()
            # mengatur header "location" pada respons untuk menunjukkan lokasi data yang telah diperbarui
            response.headers["Location"] = f"/mahasiswa/{m.nim}"
        else:
            # jika data mahasiswa tidak ditemukan, muncul HTTPException dengan status code 404
            raise HTTPException(status_code=404, detail="Item Not Found")

    except Exception as e:
        # jika terjadi kesalahan, muncul HTTPException dengan status code 500
        raise HTTPException(status_code=500, detail=f"Terjadi exception: {str(e)}")

    finally:
        # menutup koneksi ke database
        con.close()

    # mengembalikan data mahasiswa yang telah diperbarui
    return m

@app.patch("/update_mhs_patch/{nim}", response_model=MhsPatch)  # mendefinisikan route HTTP PATCH /update_mhs_put/{nim} untuk memperbarui data mahasiswa
def update_mhs_patch(nim: str, m: MhsPatch, response: Response):
    try:
        print(str(m))
        # nama database 
        DB_NAME = "upi.db"
        # membuat koneksi ke database 
        con = sqlite3.connect(DB_NAME)
        # membuat objek cursor untuk eksekusi perintah sql
        cur = con.cursor()

        # memeriksa apakah data mahasiswa dengan nim tertentu ada dalam database
        cur.execute("SELECT * FROM mahasiswa WHERE nim = ?", (nim,))
        existing_item = cur.fetchone()

    except Exception as e:
        # jika terjadi kesalahan, raise HTTPException dengan status code 500
        raise HTTPException(status_code=500, detail=f"Terjadi exception: {str(e)}")

    if existing_item:  # jika data ada, lakukan update
        sqlstr = "UPDATE mahasiswa SET "
        updates = []

        # memeriksa setiap field yang akan diupdate
        if m.nama != "kosong" and m.nama is not None:
            updates.append(f"nama = '{m.nama}'")

        if m.angkatan != "kosong" and m.angkatan is not None:
            updates.append(f"angkatan = '{m.angkatan}'")

        if m.id_prov != "kosong" and m.id_prov is not None:
            updates.append(f"id_prov = '{m.id_prov}'")

        if m.tinggi_badan != -9999 and m.tinggi_badan is not None:
            updates.append(f"tinggi_badan = {m.tinggi_badan}")

        # menggabungkan semua field yang akan diupdate menjadi satu string sql
        sqlstr += ", ".join(updates)
        sqlstr += f" WHERE nim = '{nim}'"

        print(sqlstr) # debug

        try:
            # melakukan update data mahasiswa
            cur.execute(sqlstr)  # menghapus data mahasiswa dari tabel berdasarkan nim yang diberikan
            con.commit()  # commit perubahan 
            # mengatur header "location" pada respons untuk menunjukkan lokasi data yang telah diperbarui
            response.headers["Location"] = f"/mahasiswa/{nim}"

        except Exception as e:
            # jika terjadi kesalahan saat update, muncul HTTPException dengan status code 500
            raise HTTPException(status_code=500, detail=f"Terjadi exception: {str(e)}")

    else:  # Jika data tidak ditemukan, muncul HTTPException dengan status code 404
        raise HTTPException(status_code=404, detail="Item Not Found")

    # menutup koneksi ke database
    con.close()

    # mengembalikan data mahasiswa yang telah diperbarui
    return m

@app.delete("/delete_mhs/{nim}")  # mendefinisikan route HTTP DELETE /delete_mhs/{nim} untuk menghapus data
def delete_mhs(nim: str):
    try:
        # nama database 
        DB_NAME = "upi.db"
        # membuat koneksi ke database 
        con = sqlite3.connect(DB_NAME)
        # Membuat objek cursor untuk eksekusi perintah sql
        cur = con.cursor()
        # membuat string sql untuk menghapus data mahasiswa dengan nim tertentu
        sqlstr = f"DELETE FROM mahasiswa WHERE nim = '{nim}'"
        print(sqlstr)  # debug
        cur.execute(sqlstr)  # menghapus data mahasiswa dari tabel berdasarkan nim yang diberikan
        con.commit()  # commit perubahan 
    except Exception as e:
        # jika terjadi kesalahan, muncul HTTPException dengan status code 500
        return {"status": f"terjadi error: {e}"}
    finally:
        # menutup koneksi ke database
        con.close()
    # mengembalikan status berhasil jika penghapusan berhasil
    return {"status": "ok"}

@app.post("/uploadimage")  # mendefinisikan route untuk mengunggah file gambar
def upload(file: UploadFile = File(...)):  # menerima file UploadFile melalui parameter file
    try:
        print("Mulai upload")  # mencetak pesan "Mulai upload"
        print(file.filename)  # mencetak nama file yang diunggah
        contents = file.file.read()  # membaca konten file yang diunggah
        with open("./data_file/" + file.filename, 'wb') as f:  # membuka file untuk ditulis dalam mode binary
            f.write(contents)  # menulis konten file ke file yang dibuka
    except Exception:  # menangkap exception jika terjadi kesalahan saat upload
        return {"message": "Error upload file"}  # mengembalikan pesan error jika terjadi kesalahan
    finally:
        file.file.close()  # menutup file yang diunggah
    return {"message": f"Upload berhasil: {file.filename}"}  # mengembalikan pesan berhasil upload beserta nama file

@app.get("/getimage/{nama_file}")  # mendefinisikan route untuk mengambil file gambar berdasarkan nama file
async def get_image(nama_file: str):  # menerima nama file sebagai parameter
    return FileResponse("./data_file/" + nama_file)  # mengembalikan file gambar dengan nama file yang sesuai