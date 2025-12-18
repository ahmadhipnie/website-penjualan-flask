from flask import Blueprint, render_template, request, session, redirect, url_for, make_response
from model.Laporan import Laporan
from datetime import datetime
from io import BytesIO
import xlsxwriter

laporan_bp = Blueprint('laporan', __name__, url_prefix='/admin/laporan')

@laporan_bp.route('/')
def index():
    """Menampilkan halaman laporan transaksi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    # Ambil parameter filter dari request
    status = request.args.get('status', 'semua')
    tanggal_dari = request.args.get('tanggal_dari', '')
    tanggal_sampai = request.args.get('tanggal_sampai', '')
    
    # Ambil data transaksi dengan filter
    transaksis = Laporan.get_transaksi_filtered(
        status=status if status != 'semua' else None,
        tanggal_dari=tanggal_dari if tanggal_dari else None,
        tanggal_sampai=tanggal_sampai if tanggal_sampai else None
    )
    
    # Hitung total
    total_transaksi = len(transaksis)
    total_pendapatan = sum(t['total_harga'] for t in transaksis)
    
    # Ambil summary per status
    summary = Laporan.get_summary_by_status()
    
    return render_template('admin/laporan/index.html', 
                         transaksis=transaksis,
                         total_transaksi=total_transaksi,
                         total_pendapatan=total_pendapatan,
                         summary=summary,
                         status_filter=status,
                         tanggal_dari=tanggal_dari,
                         tanggal_sampai=tanggal_sampai,
                         user=session)

@laporan_bp.route('/export-excel')
def export_excel():
    """Export laporan ke Excel"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    # Ambil parameter filter
    status = request.args.get('status', 'semua')
    tanggal_dari = request.args.get('tanggal_dari', '')
    tanggal_sampai = request.args.get('tanggal_sampai', '')
    
    # Ambil data transaksi
    transaksis = Laporan.get_transaksi_filtered(
        status=status if status != 'semua' else None,
        tanggal_dari=tanggal_dari if tanggal_dari else None,
        tanggal_sampai=tanggal_sampai if tanggal_sampai else None
    )
    
    # Buat file Excel di memory
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Laporan Transaksi')
    
    # Format
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4e73df',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    cell_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })
    
    number_format = workbook.add_format({
        'border': 1,
        'align': 'right',
        'num_format': '#,##0'
    })
    
    # Header
    headers = ['No', 'Kode Transaksi', 'Tanggal', 'Customer', 'Email', 'No. Telepon', 
               'Status', 'Ekspedisi', 'No. Resi', 'Total Harga']
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Data
    for row, transaksi in enumerate(transaksis, start=1):
        worksheet.write(row, 0, row, cell_format)
        worksheet.write(row, 1, transaksi['kode_transaksi'], cell_format)
        worksheet.write(row, 2, transaksi['created_at'].strftime('%d-%m-%Y %H:%M'), cell_format)
        worksheet.write(row, 3, transaksi['nama_customer'], cell_format)
        worksheet.write(row, 4, transaksi['email'], cell_format)
        worksheet.write(row, 5, transaksi['nomor_telepon'], cell_format)
        worksheet.write(row, 6, transaksi['status'].replace('_', ' ').title(), cell_format)
        worksheet.write(row, 7, transaksi['nama_ekspedisi'] if transaksi['nama_ekspedisi'] else '-', cell_format)
        worksheet.write(row, 8, transaksi['nomor_resi'] if transaksi['nomor_resi'] else '-', cell_format)
        worksheet.write(row, 9, transaksi['total_harga'], number_format)
    
    # Total
    total_row = len(transaksis) + 1
    worksheet.write(total_row, 8, 'TOTAL:', header_format)
    worksheet.write(total_row, 9, sum(t['total_harga'] for t in transaksis), number_format)
    
    # Set column width
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 18)
    worksheet.set_column('D:D', 25)
    worksheet.set_column('E:E', 30)
    worksheet.set_column('F:F', 15)
    worksheet.set_column('G:G', 20)
    worksheet.set_column('H:H', 25)
    worksheet.set_column('I:I', 15)
    worksheet.set_column('J:J', 15)
    
    workbook.close()
    output.seek(0)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'Laporan_Transaksi_{timestamp}.xlsx'
    
    # Send file
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

@laporan_bp.route('/export-pdf')
def export_pdf():
    """Export laporan ke PDF"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    
    try:
        from fpdf import FPDF
    except ImportError:
        return "Library FPDF belum terinstall. Install dengan: pip install fpdf", 500
    
    # Ambil parameter filter
    status = request.args.get('status', 'semua')
    tanggal_dari = request.args.get('tanggal_dari', '')
    tanggal_sampai = request.args.get('tanggal_sampai', '')
    
    # Ambil data transaksi
    transaksis = Laporan.get_transaksi_filtered(
        status=status if status != 'semua' else None,
        tanggal_dari=tanggal_dari if tanggal_dari else None,
        tanggal_sampai=tanggal_sampai if tanggal_sampai else None
    )
    
    # Buat PDF
    pdf = FPDF('L', 'mm', 'A4')  # Landscape
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Title
    pdf.cell(0, 10, 'LAPORAN TRANSAKSI', 0, 1, 'C')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f'Periode: {tanggal_dari if tanggal_dari else "Semua"} s/d {tanggal_sampai if tanggal_sampai else "Semua"}', 0, 1, 'C')
    pdf.cell(0, 5, f'Status: {status.replace("_", " ").title() if status != "semua" else "Semua"}', 0, 1, 'C')
    pdf.ln(5)
    
    # Table Header
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(10, 7, 'No', 1, 0, 'C')
    pdf.cell(35, 7, 'Kode Transaksi', 1, 0, 'C')
    pdf.cell(30, 7, 'Tanggal', 1, 0, 'C')
    pdf.cell(40, 7, 'Customer', 1, 0, 'C')
    pdf.cell(30, 7, 'Status', 1, 0, 'C')
    pdf.cell(40, 7, 'Ekspedisi', 1, 0, 'C')
    pdf.cell(30, 7, 'No. Resi', 1, 0, 'C')
    pdf.cell(30, 7, 'Total', 1, 1, 'C')
    
    # Table Data
    pdf.set_font('Arial', '', 7)
    total = 0
    for idx, transaksi in enumerate(transaksis, start=1):
        pdf.cell(10, 6, str(idx), 1, 0, 'C')
        pdf.cell(35, 6, transaksi['kode_transaksi'], 1, 0, 'L')
        pdf.cell(30, 6, transaksi['created_at'].strftime('%d-%m-%Y'), 1, 0, 'C')
        pdf.cell(40, 6, transaksi['nama_customer'][:25], 1, 0, 'L')
        pdf.cell(30, 6, transaksi['status'].replace('_', ' ').title()[:20], 1, 0, 'L')
        pdf.cell(40, 6, (transaksi['nama_ekspedisi'] if transaksi['nama_ekspedisi'] else '-')[:25], 1, 0, 'L')
        pdf.cell(30, 6, (transaksi['nomor_resi'] if transaksi['nomor_resi'] else '-')[:20], 1, 0, 'L')
        pdf.cell(30, 6, f"Rp {transaksi['total_harga']:,.0f}".replace(',', '.'), 1, 1, 'R')
        total += transaksi['total_harga']
    
    # Total
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(215, 7, 'TOTAL', 1, 0, 'C')
    pdf.cell(30, 7, f"Rp {total:,.0f}".replace(',', '.'), 1, 1, 'R')
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'Laporan_Transaksi_{timestamp}.pdf'
    
    # Send PDF
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response
