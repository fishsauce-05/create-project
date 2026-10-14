import threading
from typing import override
from concurrency.runner import BackgroundRunner

class ThreadedBackgroundRunner(BackgroundRunner):
	def __init__(self, post):
		self._post = post

	@override
	def run(self, work, on_success, on_error):
		def _target():
			try:
				work()
			except Exception as e:
				self._post(partial(on_error, e))
				return
			self._post(on_success)

		threading.Thread(target=_target, daemon=True).start()
