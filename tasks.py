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
    download_csv_file()
    read_csv_file()
    close_annoying_modal()
    fill_the_form()
    # save_preview_screenshot()


def open_robot_order_website():
    """
    Opens RobotSpareBin Industries Inc. robot order website.
    """
    url = "https://robotsparebinindustries.com/#/robot-order"
    browser.goto(url)


def download_csv_file():
    """
    Downloads CSV file
    """
    url = "https://robotsparebinindustries.com/orders.csv"
    http = HTTP()
    http.download(url, overwrite=True)


def read_csv_file():
    """
    Reads the downloaded CSV file
    """
    csv = Tables()
    worksheet = csv.read_table_from_csv(path="orders.csv", header=True)
    orders = get_orders(worksheet)
    return orders


def get_orders(worksheet):
    """Get orders from the CSV file"""
    for row in worksheet:
        fill_the_form(row)


def close_annoying_modal():
    """
    Closes the annoying modal appearing on page load
    """
    page = browser.page()
    page.click('//*[@id="root"]/div/div[2]/div/div/div/div/div/button[1]')


def fill_the_form(row):
    """Fill the Head, Body, Legs and Address fields"""
    page = browser.page()
    page.select_option("#head.custom-select", row["Head"])
    page.check(f"#id-body-{row['Body']}")
    page.select_option(
        'input.form-control[placeholder="Enter the part number for the legs"][required=""]',
        row["Legs"],
    )
    page.fill("#address.form-control", row["Address"])

# def save_preview_screenshot():
#     """Save a preview screenshot of the robot"""
#     page = browser.page()
#     page.click("#preview.btn.btn-secondary")
#     page.screenshot("output/preview.png")
