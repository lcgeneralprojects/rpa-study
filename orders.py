from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables

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
            page.click("#order-another")
            close_annoying_modal()
            break