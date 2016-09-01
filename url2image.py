#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


# TODO: сделать также PyQt5 вариант
# TODO: проверять поддерживаемые форматы по суффиксу file_name, если формат не поддерживается,
# кидать исключение с описание поддерживаемых параметров


from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtGui import QApplication, QImage, QPainter
from PyQt4.QtCore import QEventLoop, QSize, QUrl
from PyQt4.QtNetwork import QNetworkProxyFactory

# Чтобы не было проблем запуска компов с прокси
QNetworkProxyFactory.setUseSystemConfiguration(True)


class WebPage(QWebPage):
    def userAgentForUrl(self, url):
        return 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0'


qApp = None


def load_pyqt4_plugins():
    """
    Функция загружает Qt плагины.

    """

    import PyQt4
    import os

    qApp = PyQt4.QtGui.QApplication.instance()

    for plugins_dir in [os.path.join(p, "plugins") for p in PyQt4.__path__]:
        qApp.addLibraryPath(plugins_dir)


# TODO: обрабатывать ошибки, возникающие при ошибке загрузки
def url2image(url, file_name=None):
    """Function at the specified url downloads the page and stores it QImage object and returns it.
    If you pass file_name, then the function will save the picture in the file.

    Функция по указанному url загружает страницу и сохраняет ее объект QImage и возвращает его.
    Если передать file_name, тогда функция сохранит в файл картинку.
    """

    # Нужно создавать только один раз
    global qApp
    if qApp is None:
        qApp = QApplication([])

        # Пришлось добавить из-за того, что картинки не прогружались
        load_pyqt4_plugins()

    # TODO: прятать вертикальный и горизонтальный ползунки
    # Загрузка url и ожидание ее
    view = QWebView()
    view.setPage(WebPage())
    # view.show()

    view.load(QUrl(url))
    loop = QEventLoop()
    view.loadFinished.connect(loop.quit)
    loop.exec_()

    # Запрашиваем через javascript размеры страницы сайта
    width = view.page().mainFrame().evaluateJavaScript("window.document.body.scrollWidth")
    height = view.page().mainFrame().evaluateJavaScript("window.document.body.scrollHeight")

    # Устанавливаем границы документа
    view.page().setViewportSize(QSize(width, height))

    img = QImage(width, height, QImage.Format_ARGB32)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.HighQualityAntialiasing)
    view.page().mainFrame().render(painter)
    painter.end()

    if file_name:
        img.save(file_name)

    # qApp.exec()

    return img


if __name__ == '__main__':
    img = url2image('https://www.google.ru/search?q=google+qwidget')
    img.save("html.png")
    # # Or:
    # img = url2image('https://www.google.ru/search?q=google+qwidget', "html.png")

    url2image('https://www.google.ru/search?q=cats&tbm=isch', 'cats.png')

    # TODO: слишком большая высота получилась, нужно разобраться
    url2image('https://en.wikipedia.org/wiki/Python_(programming_language)', 'wiki.jpg')

    # TODO: бот вернул картинку размером 200x2500, т.к. телеграмм уменьшил ее в 3 раза
    url2image('http://bash.im/', 'bash.png')
