from abc import ABC, abstractmethod
from typing import Callable

class BackgroundRunner(ABC):
	@abstractmethod
	def run(self, work: Callable[[], None], on_success: Callable[[], None], on_error: Callable[[Exception], None]) -> None:
		pass