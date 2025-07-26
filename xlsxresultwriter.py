import xlsxwriter
import time
from chargeampsdata import ChargingSession
from datetime import datetime
import os
from io import BytesIO


class XlsxResult:
    """
    Class to generate an xlsx file with charging sessions data."""

    def __init__(self):
        """
        Initialize the XlsxResult class."""
        return None

    def gen_output_file(self, charge_sessions: list[ChargingSession],
                        kwh_price: float) -> BytesIO:
        """
        Generates an xlsx file with the charging sessions data.
        :param charge_sessions: List of ChargingSession objects
        :param kwh_price: Price per kWh in cents
        :return: BytesIO object containing the xlsx file
        """
        output = BytesIO()

        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Charging Summary")
        #Formats
        header_format = workbook.add_format({
            'align': 'center',
            'bold': True,
            'bottom': True,
            'border': 2
        })
        cell_format = workbook.add_format({
            'align': 'center',
            'bold': False,
            'bottom': True,
            'border': 1
        })
        euros = workbook.add_format({
            'align': 'center',
            'num_format': '#,##0.00€',
            'bottom': True,
            'border': 1
        })
        cents = workbook.add_format({'num_format': '#,##0 cents'})
        date_format = workbook.add_format({
            'align': 'center',
            'num_format': 'yyyy-mm-d hh:mm',
            'bottom': True,
            'border': 1
        })  #2024-12-09T05:35:32

        worksheet.write(0, 0, "No of Charging Process", header_format)
        worksheet.write(0, 1, "Start", header_format)
        worksheet.write(0, 2, "End", header_format)
        worksheet.write(0, 3, "RFID tag", header_format)
        worksheet.write(0, 4, "kWh", header_format)
        worksheet.write(0, 5, "cent/kWh", header_format)
        worksheet.write(0, 6, "total costs", header_format)
        row = 1
        idx = 1
        for csession in charge_sessions:
            worksheet.write_number(row, 0, idx, cell_format)
            worksheet.write_datetime(row, 1, csession.start_time, date_format)
            worksheet.write_datetime(row, 2, csession.end_time, date_format)
            worksheet.write_string(row, 3, csession.rfid, cell_format)
            worksheet.write_number(row, 4, csession.total_consumption_kwh,
                                   cell_format)
            worksheet.write_number(row, 5, float(kwh_price), cell_format)
            worksheet._write_formula(
                row, 6,
                "=E" + str(row + 1) + "*" + "F" + str(row + 1) + "/100", euros)
            row += 1
            idx += 1
        worksheet.write_string(row, 5, "Total Costs", header_format)
        worksheet._write_formula(row, 6, "=SUM(G2:G" + str(idx - 1) + ")",
                                 header_format)

        workbook.close()
        output.seek(0)
        return output
