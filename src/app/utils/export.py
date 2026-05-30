import csv
import io
from datetime import datetime

from flask import make_response


def csv_response(rows, filename, fieldnames):
    """Return a CSV file download response."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{filename}_{datetime.utcnow().strftime("%Y%m%d")}.csv"'
    )
    return response
