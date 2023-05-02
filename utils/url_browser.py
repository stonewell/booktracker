import logging

import sys
from multiprocessing import Process, Queue, freeze_support
from threading import Thread
from io import StringIO

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl, Slot, Signal, QObject
from PySide6.QtWebEngineWidgets import QWebEngineView


class UrlBrowserEngine(QObject):
  run_in_ui_thread_signal_ = Signal(object)

  def __init__(self, task_queue, output_queue):
    super().__init__()

    self.app_ = QApplication(sys.argv)
    self.web_engine_view_ = QWebEngineView()
    self.web_engine_view_.loadFinished.connect(self.__on_load_finished)
    self.run_in_ui_thread_signal_.connect(self.__run_in_ui_thread)
    self.task_queue_ = task_queue
    self.output_queue_ = output_queue

  @Slot()
  def __on_load_finished(self):
    self.web_engine_view_.page().runJavaScript(
        "document.documentElement.outerHTML", 0, self.__on_html)

  @Slot(object)
  def __run_in_ui_thread(self, obj):
    if callable(obj):
      obj()

  def __on_html(self, html):
    print(html)
    self.output_queue_.put(html)

  def load_url(self, url, timeout, extra_headers):
    self.run_in_ui_thread_signal_.emit(
        lambda: self.__load_url(url, timeout, extra_headers))

  def __load_url(self, url, timeout, extra_headers):
    del timeout
    del extra_headers

    self.web_engine_view_.load(QUrl(url))

  def quit(self):
    logging.debug('quit browser process')
    self.run_in_ui_thread_signal_.emit(QApplication.quit)

  def run(self):
    self.app_.exec()


class UrlBrowser:

  def __init__(self):
    self.task_queue_ = Queue()
    self.output_queue_ = Queue()
    self.browser_ = None

  def open_url(self, url, timeout, extra_headers):
    self.task_queue_.put((url, timeout, extra_headers))

    return StringIO(self.output_queue_.get())

  def start(self):
    logging.debug('start url browser')
    freeze_support()

    self.browser_ = Process(target=browser_worker,
                            args=(self.task_queue_, self.output_queue_))
    self.browser_.start()

  def stop(self):
    logging.debug('stop url browser')
    self.task_queue_.put('STOP')
    self.browser_.join()
    logging.debug('url browser stopped')


def task_worker(engine):
  for args in iter(engine.task_queue_.get, 'STOP'):
    engine.load_url(*args)

  engine.quit()


def browser_worker(task_queue, output_queue):
  engine_ = UrlBrowserEngine(task_queue, output_queue)

  task_worker_ = Thread(target=task_worker, args=(engine_, ))
  task_worker_.start()

  engine_.run()
  task_worker_.join()
  logging.debug('task work quit')
