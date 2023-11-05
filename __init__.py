from anki.hooks import wrap
from aqt.sound import (
    av_player,
    MpvManager,
    OnDoneCallback,
    AVTag,
    SoundOrVideoTag,
)
from aqt import AnkiQt
from aqt.qt import (
    QAction,
    QHBoxLayout,
    QVBoxLayout,
    QDialog,
    QDialogButtonBox,
    QSlider,
    QLabel,
    Qt,
)
from aqt import mw
from aqt.utils import qconnect
from anki import hooks
from aqt import gui_hooks
import os

config = mw.addonManager.getConfig(__name__)


class Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio volume")
        self.volume = config["volume"]

        self.layout = QVBoxLayout()
        self.layout1 = QHBoxLayout()
        self.layout2 = QHBoxLayout()

        QBtn = (
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setSingleStep(5)
        self.slider.setValue(self.volume)
        self.slider.valueChanged.connect(self.value_changed)

        self.label = QLabel(f"{self.volume}%")

        self.layout1.addWidget(self.slider)
        self.layout1.addWidget(self.label)
        self.layout2.addWidget(self.buttonBox)
        self.layout.addLayout(self.layout1)
        self.layout.addLayout(self.layout2)
        self.setLayout(self.layout)

    def accept(self):
        config["volume"] = self.volume
        mw.addonManager.writeConfig(__name__, config)
        self.close()

    def value_changed(self, v):
        self.volume = v
        self.label.setText(f"{self.volume}%")
        self.slider.setValue(self.volume)


def testFunction() -> None:
    dlg = Dialog()
    dlg.exec()


action = QAction("Audio volume", mw)
qconnect(action.triggered, testFunction)
mw.form.menuTools.addAction(action)


class ModifiedMpvManager(MpvManager):
    def play(self, tag: AVTag, on_done: OnDoneCallback) -> None:
        assert isinstance(tag, SoundOrVideoTag)
        self._on_done = on_done
        filename = hooks.media_file_filter(tag.filename)
        path = os.path.join(self.media_folder, filename)

        self.command(
            "loadfile",
            path,
            "replace",
            f"volume={config['volume']}," + "pause=no,",
        )
        gui_hooks.av_player_did_begin_playing(self, tag)


def add_player(_):
    av_player.players.append(
        ModifiedMpvManager(mw.pm.base, mw.col.media.dir())
    )


AnkiQt.setup_sound = wrap(AnkiQt.setup_sound, add_player, "after")
