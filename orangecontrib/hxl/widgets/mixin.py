from AnyQt.QtWidgets import QTextEdit

from orangecontrib.hxl.widgets.utils import browse_local_resource


class HXLWidgetFeedbackMixin:
    _base_active: str = None
    feedback: QTextEdit = None

    def browse_active(self):
        """browse_active
        Used for browse active RAWFile or RAWFileCollection
        """
        if self._base_active:
            browse_local_resource(self._base_active)
        else:
            self.feedback.setPlainText('Invalid base')
