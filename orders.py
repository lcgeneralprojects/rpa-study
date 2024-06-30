from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

import os

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    # TODO: Archive the receipts into individual archives?
    # archive_receipts()


def open_robot_order_website():
    """Navigates to the given URL and accesses the orders file"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order/")
    close_annoying_modal()
    orders = get_orders()
    for order in orders:
        fill_the_form(order)
    

def get_orders():
    """Downloads the orders file"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    return library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    

def close_annoying_modal():
    """Closes the forced modal window upon entering the robot-ordering page"""
    page = browser.page()
    page.click(".btn-danger")
    
    
def fill_the_form(order):
    """Fills the order form, previews, and submits the order"""
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.check("#id-body-"+str(order["Body"]))
    # page.fill("placeholder=\"Enter the part number for the legs\"", str(order["Legs"]))
    # "//button[@routerlink='/web/click']"
    # page.locator("placeholder=Enter the part number for the legs").fill(str(order["Legs"]))
    # page.fill("//button[@placeholder=\"Enter the part number for the legs\"]", str(order["Legs"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", str(order["Address"]))
    page.click("#preview")
    while True:
        page.click("#order")
        if page.query_selector("#order-another"):
            screenshot_path = screenshot_robot(str(order["Order number"]))
            pdf_path = store_receipt_as_pdf(str(order["Order number"]))
            embed_screenshot_to_receipt(screenshot=screenshot_path, pdf_file=pdf_path)
            page.click("#order-another")
            close_annoying_modal()
            break
        

def store_receipt_as_pdf(order_number):
    """Saves the order as a pdf file"""
    page = browser.page()
    pdf = PDF()
    order_html = page.locator("#receipt").inner_html()
    pdf_path = os.path.join("output", "receipts", order_number, '.pdf')
    pdf.html_to_pdf(order_html, pdf_path)
    return pdf_path


def screenshot_robot(order_number):
    """Saves a screenshot of the order"""
    # TODO: Currently, the browser is too small to screenshot the entire image of a robot
    page = browser.page()
    screenshot_path = os.path.join("output", "receipts", order_number, '.png')
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds a screenshot of the robot into the pdf file of the receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(screenshot, pdf_file, pdf_file)
    

# TODO: deal with ValueError: No files found to archive
# def archive_receipts():
#     """Archives the receipts"""
#     lib = Archive()
#     # receipt_path = os.path.join(".", "output", "receipts")
#     # archive_path = os.path.join(".", "output", "receipts.zip")
#     lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")