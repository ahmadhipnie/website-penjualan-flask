from flask import Flask, render_template, session, redirect, url_for, g
from model.database import get_db
from controller.auth.AuthController import auth_bp
from controller.admin.KategoriController import kategori_bp
from controller.admin.ProdukController import produk_bp
from controller.landing.LandingController import landing_bp
from controller.admin.JenisEkspedisiController import jenis_ekspedisi_bp
from controller.customer.DashboardCustomerController import customer_bp
from controller.admin.TransaksiController import transaksi_bp
from controller.admin.LaporanController import laporan_bp
import os

app = Flask(__name__)

# Konfigurasi Secret Key untuk Session
app.secret_key = os.urandom(24)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'penjualan_flask'

# Close koneksi setelah selesai request
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(kategori_bp)
app.register_blueprint(produk_bp)
app.register_blueprint(landing_bp, url_prefix='/landing')
app.register_blueprint(jenis_ekspedisi_bp)
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(transaksi_bp)
app.register_blueprint(laporan_bp)

# Route halaman utama
@app.route('/')
def index():
    if 'user_id' in session:
        # Jika sudah login, redirect sesuai role
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    # Redirect ke landing page jika belum login
    return redirect(url_for('landing.index'))

# Route dashboard admin
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard/index.html', user=session)

# Route dashboard customer
@app.route('/customer/dashboard')
def customer_dashboard():
    if 'user_id' not in session or session.get('role') != 'customer':
        return redirect(url_for('auth.login'))
    return redirect(url_for('customer.dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
