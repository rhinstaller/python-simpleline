#!/bin/python3

from simpleline.base import App, UIScreen


class MyApp(App):
    def application_quit_cb(self):
        """Show message to user when quitting application"""
        print("Application is closing. Bye!")


class HelloWorld(UIScreen):
    title = u"Hello World" # title is printed if there is nothing else


if __name__ == "__main__":
    a = MyApp("Hello World")
    s = HelloWorld(a)
    a.schedule_screen(s)
    a.run()
