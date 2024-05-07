from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    browser.configure(slowmo=100)
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        order_number = row["Order number"]
        close_annoying_modal()
        fill_the_form(row)
        screenshot = screenshot_robot(order_number)
        pdf_file = store_receipt_as_pdf(order_number)
        embed_screenshot_to_receipt(screenshot, pdf_file)
    archive_receipts()


def open_robot_order_website():
    """
    Opens RobotSpareBin Industries Inc. robot order website.
    """
    url = "https://robotsparebinindustries.com/#/robot-order"
    browser.goto(url)


def get_orders():
    """Get orders from the CSV file"""
    url = "https://robotsparebinindustries.com/orders.csv"
    http = HTTP()
    http.download(url, overwrite=True)

    csv = Tables()
    orders = csv.read_table_from_csv(path="orders.csv", header=True)
    return orders


def close_annoying_modal():
    """
    Closes the annoying modal appearing on page load
    """
    page = browser.page()
    ok_button_locator = "text=OK"
    ok_button_visible = page.is_visible(ok_button_locator)
    if ok_button_visible:
        page.click(ok_button_locator)


def fill_the_form(row):
    """Fill the Head, Body, Legs and Address fields"""
    page = browser.page()
    page.select_option("#head", row["Head"])
    page.check(f"#id-body-{row['Body']}")
    page.fill(
        'input.form-control[placeholder="Enter the part number for the legs"][required=""]',
        row["Legs"],
    )
    page.fill("#address", row["Address"])

    # Preview the robot
    page.click('text="Preview"')
    page.wait_for_selector("text=Admire your robot!")

    # Submit the order
    page.click('text="Order"')
    while not page.is_visible("#receipt"):
        page.click("text='Order'")


def screenshot_robot(order_number):
    """Take a screenshot of the robot"""
    page = browser.page()
    screenshot_file = f"output/screenshots/robot_{order_number}.png"
    page.screenshot(path=screenshot_file)
    return screenshot_file


def store_receipt_as_pdf(order_number):
    """Store the receipt as a PDF file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_file = f"output/receipts/order_{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_file)
    page.click('text="Order another robot"')
    return pdf_file


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the screenshot to the PDF receipt"""
    pdf = PDF()
    files = [screenshot]
    pdf.add_files_to_pdf(files=files, target_document=pdf_file, append=True)


def archive_receipts():
    """Create ZIP archive of the receipts"""
    archive = Archive()
    archive.archive_folder_with_zip("output/receipts", "output/robot_orders.zip")
