from AnyQt.QtWidgets import QTextEdit
from AnyQt.QtWidgets import QMessageBox
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
            QMessageBox.warning(
                self,
                "Browse local data for resource",
                "No resource to preview at Data Vault")
            return None
            # self.feedback.setPlainText('Invalid base')
