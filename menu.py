from urllib.request import urlretrieve
import os.path
import datetime
import fitz
from PIL import Image, ImageTk
import tkinter as tk
from holidays import CZ


def remove_old_files():
    menu = './menu.pdf'
    check_menu = os.path.isfile(menu)

    if check_menu:
        print("Removing old menu.pdf and pages...")
        os.remove(menu)
        try:
            os.remove("./1_page.png")
            os.remove("./2_page.png")
        except:
            pass


def get_new_menu():
    try:
        print("Getting new menu...")
        urlretrieve("https://www.iqrestaurant.cz/brno/menu.pdf", "menu.pdf")
    except:
        print("Failed to download menu.pdf, make sure you are connected to the internet!")


def get_pixmaps_and_save_as_png(page1, page2):
    # GET PIXELMAP OF THE PAGES
    page1_img = page1.get_pixmap()
    page2_img = page2.get_pixmap()

    # SAVING THE PIXELMAPS INTO PNG FILES
    page1_img.save("1_page.png")
    page2_img.save("2_page.png")


def handle_and_display_images():
    # LOAD IMAGES
    page1 = Image.open("./1_page.png")
    page2 = Image.open("./2_page.png")

    # CREATING TKINTER WINDOW
    window = tk.Tk()

    # GETTING SCREEN WIDTH AND HEIGHT
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # RESIZING IMAGES TO FIT THE SCREEN
    page1 = page1.resize((int(screen_width / 2), screen_height))
    page2 = page2.resize((int(screen_width / 2), screen_height))

    # CONVERTING IMAGES TO TKINTER COMPATIBLE FORMAT
    tk_image1 = ImageTk.PhotoImage(page1)
    tk_image2 = ImageTk.PhotoImage(page2)

    # CREATING TWO LABELS TO DISPLAY THE IMAGES
    label1 = tk.Label(window, image=tk_image1)
    label2 = tk.Label(window, image=tk_image2)

    # PLACING LABELS SIDE BY SIDE
    label1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    label2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # SETTING WINDOW TO FULLSCREEN MODE
    window.attributes('-fullscreen', True)

    # STARTING TKINTER MAIN EVENT LOOP
    window.mainloop()


def get_holiday_list():
    today = datetime.date.today()
    year = today.year

    # List of holidays (dates in yyyy,mm,dd format)
    unaltered_holiday_list = []
    for holiday in CZ(years=[year]).items():
        unaltered_holiday_list.append(holiday)

    # print(unaltered_holiday_list)

    get_holidays = [holidays[0] for holidays in unaltered_holiday_list]
    holiday_list = [d.strftime("%Y-%m-%d") for d in get_holidays]

    # print(holiday_list)

    return holiday_list


def main():
    remove_old_files()
    get_new_menu()

    # Handle downloaded pdf file
    file_handle = fitz.open("./menu.pdf")

    today = datetime.date.today()

    workdays = {
        0: [0, 1], # MONDAY
        1: [2, 3], # TUESDAY, YOU GET THE IDEA
        2: [4, 5],
        3: [6, 7],
        4: [8, 9]
    }

    holiday_list = get_holiday_list()

    days_since_monday = today.weekday()
    if days_since_monday > 4:  # IF TODAY IS A WEEKEND DAY
        days_since_monday = 0

    # CALCULATE START AND END DATES OF THIS WORK WEEK
    start_date = today - datetime.timedelta(days=days_since_monday)
    end_date = start_date + datetime.timedelta(days=4)

    # ITERATING OVER WORKDAYS
    holidays_in_workweek = 0
    for i in range((end_date - start_date).days + 1):
        date = start_date + datetime.timedelta(days=i)

        if date.strftime('%Y-%m-%d') in holiday_list:
            holidays_in_workweek += 1
            # print(f"There was a holiday on {date.strftime('%A, %B %d, %Y')}.")

            # GETTING KEY TO DELETE
            match date.strftime('%A'):
                case "Monday":
                    key_to_delete = 0
                case "Tuesday":
                    key_to_delete = 1
                case "Wednesday":
                    key_to_delete = 2
                case "Thursday":
                    key_to_delete = 3
                case "Friday":
                    key_to_delete = 4

            # DELETING THE KEY
            del workdays[key_to_delete]

            # ADJUSTING ALL NEXT VALUES BASED ON DELETED KEY
            for key, value in workdays.items():
                if key > key_to_delete:
                    workdays[key] = [value[0] - 2, value[1] - 2]

    dt = datetime.datetime.now()
    current_day = dt.weekday()

    # GETTING WHAT PAGES TO DISPLAY
    page1 = file_handle[workdays[current_day][0]]
    page2 = file_handle[workdays[current_day][1]]

    get_pixmaps_and_save_as_png(page1, page2)

    handle_and_display_images()


if __name__ == '__main__':
    main()