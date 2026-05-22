# -*- coding: utf-8 -*-
"""
Compatibility helpers for running QQuake with both QGIS 3 / Qt 5 and
QGIS 4 / Qt 6.

The helpers intentionally prefer the old API where it is still available
(QGIS 3 / PyQt5) and fall back to the scoped Qt 6 / PyQt6 enum names when
required. This keeps the plugin installable on the QGIS 3 series while
avoiding unscoped enum names removed by Qt 6.
"""

from qgis.PyQt.QtCore import Qt
try:  # PyQt5 / Qt 5
    from qgis.PyQt.QtCore import QVariant as _QVariant
except ImportError:  # PyQt6 / Qt 6
    _QVariant = None

try:
    from qgis.PyQt.QtCore import QMetaType
except ImportError:  # pragma: no cover - QMetaType is available in normal QGIS builds
    QMetaType = None

from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QFrame,
    QLayout,
    QMessageBox,
    QSizePolicy,
    QTabWidget,
    QToolButton,
)
from qgis.PyQt.QtCore import QItemSelectionModel
from qgis.core import Qgis, QgsUnitTypes, QgsBlockingNetworkRequest
try:
    from qgis.core import QgsVectorLayerTemporalProperties
except ImportError:  # QGIS versions before vector layer temporal properties
    QgsVectorLayerTemporalProperties = None


def enum_value(value):
    """Return the integer value behind a Qt/PyQGIS enum when needed."""
    return value.value if hasattr(value, 'value') else int(value)


def _enum(enum_class, scope, name, fallback_name=None):
    """Return a scoped enum value, falling back to the Qt5 unscoped name."""
    try:
        return getattr(getattr(enum_class, scope), name)
    except AttributeError:
        return getattr(enum_class, fallback_name or name)


def _qgis_enum(scope, name):
    """Return a scoped Qgis enum value, falling back to the QGIS 3 name."""
    try:
        return getattr(getattr(Qgis, scope), name)
    except AttributeError:
        return getattr(Qgis, name)


def _unit(name, fallback_name):
    """Return a scoped QgsUnitTypes distance unit, falling back to old names."""
    try:
        return getattr(QgsUnitTypes.DistanceUnit, name)
    except AttributeError:
        return getattr(QgsUnitTypes, fallback_name)


def _temporal_mode(name, fallback_name):
    if QgsVectorLayerTemporalProperties is None:
        return None
    try:
        return getattr(QgsVectorLayerTemporalProperties.Mode, name)
    except AttributeError:
        return getattr(QgsVectorLayerTemporalProperties, fallback_name)


def _blocking_network_error(name):
    try:
        return getattr(QgsBlockingNetworkRequest.ErrorCode, name)
    except AttributeError:
        return getattr(QgsBlockingNetworkRequest, name)


def _meta_type(name, fallback_name):
    """Return a field type usable by QgsField in Qt5 and Qt6 builds."""
    if _QVariant is not None:
        return getattr(_QVariant, fallback_name)

    if QMetaType is None:
        raise ImportError('Neither QVariant nor QMetaType is available')

    try:
        return getattr(QMetaType.Type, name)
    except AttributeError:
        return getattr(QMetaType, name)


class QVariant:  # pylint: disable=too-few-public-methods
    """Subset of QVariant type constants used by QQuake.

    Qt 6/PyQt6 plugin code should use QMetaType.Type for field definitions,
    but QGIS 3/PyQt5 still exposes and accepts QVariant.Type values. This
    shim preserves the existing QQuake code style while returning the correct
    type constants for the current runtime.
    """

    String = _meta_type('QString', 'String')
    Int = _meta_type('Int', 'Int')
    Double = _meta_type('Double', 'Double')
    Time = _meta_type('QTime', 'Time')
    DateTime = _meta_type('QDateTime', 'DateTime')
    Date = _meta_type('QDate', 'Date')
    Bool = _meta_type('Bool', 'Bool')
    Invalid = _meta_type('UnknownType', 'Invalid')


QT_ISO_DATE = _enum(Qt, 'DateFormat', 'ISODate', 'ISODate')
QT_UTC = _enum(Qt, 'TimeSpec', 'UTC', 'UTC')
QT_HORIZONTAL = _enum(Qt, 'Orientation', 'Horizontal', 'Horizontal')
QT_WA_DELETE_ON_CLOSE = _enum(Qt, 'WidgetAttribute', 'WA_DeleteOnClose', 'WA_DeleteOnClose')

QT_DISPLAY_ROLE = enum_value(_enum(Qt, 'ItemDataRole', 'DisplayRole', 'DisplayRole'))
QT_CHECK_STATE_ROLE = enum_value(_enum(Qt, 'ItemDataRole', 'CheckStateRole', 'CheckStateRole'))
QT_FONT_ROLE = enum_value(_enum(Qt, 'ItemDataRole', 'FontRole', 'FontRole'))
QT_USER_ROLE = enum_value(_enum(Qt, 'ItemDataRole', 'UserRole', 'UserRole'))

QT_CHECKED = _enum(Qt, 'CheckState', 'Checked', 'Checked')
QT_UNCHECKED = _enum(Qt, 'CheckState', 'Unchecked', 'Unchecked')

QT_ITEM_IS_ENABLED = _enum(Qt, 'ItemFlag', 'ItemIsEnabled', 'ItemIsEnabled')
QT_ITEM_IS_SELECTABLE = _enum(Qt, 'ItemFlag', 'ItemIsSelectable', 'ItemIsSelectable')
QT_ITEM_IS_EDITABLE = _enum(Qt, 'ItemFlag', 'ItemIsEditable', 'ItemIsEditable')
QT_ITEM_IS_USER_CHECKABLE = _enum(Qt, 'ItemFlag', 'ItemIsUserCheckable', 'ItemIsUserCheckable')

QT_MATCH_CONTAINS = _enum(Qt, 'MatchFlag', 'MatchContains', 'MatchContains')
QT_MATCH_EXACTLY = _enum(Qt, 'MatchFlag', 'MatchExactly', 'MatchExactly')
QT_MATCH_RECURSIVE = _enum(Qt, 'MatchFlag', 'MatchRecursive', 'MatchRecursive')

QT_BUTTON_OK = _enum(QDialogButtonBox, 'StandardButton', 'Ok', 'Ok')
QT_BUTTON_CANCEL = _enum(QDialogButtonBox, 'StandardButton', 'Cancel', 'Cancel')
QT_BUTTON_CLOSE = _enum(QDialogButtonBox, 'StandardButton', 'Close', 'Close')
QT_MESSAGEBOX_YES = _enum(QMessageBox, 'StandardButton', 'Yes', 'Yes')

QT_SELECTION_CLEAR_AND_SELECT = _enum(QItemSelectionModel, 'SelectionFlag', 'ClearAndSelect', 'ClearAndSelect')

QT_SIZE_POLICY_MINIMUM = _enum(QSizePolicy, 'Policy', 'Minimum', 'Minimum')
QT_SIZE_POLICY_FIXED = _enum(QSizePolicy, 'Policy', 'Fixed', 'Fixed')
QT_SIZE_POLICY_EXPANDING = _enum(QSizePolicy, 'Policy', 'Expanding', 'Expanding')
QT_SIZE_POLICY_PREFERRED = _enum(QSizePolicy, 'Policy', 'Preferred', 'Preferred')

QT_COMBOBOX_NO_INSERT = _enum(QComboBox, 'InsertPolicy', 'NoInsert', 'NoInsert')
QT_FRAME_NO_FRAME = _enum(QFrame, 'Shape', 'NoFrame', 'NoFrame')
QT_FRAME_PLAIN = _enum(QFrame, 'Shadow', 'Plain', 'Plain')
QT_TAB_POSITION_NORTH = _enum(QTabWidget, 'TabPosition', 'North', 'North')
QT_TOOLBUTTON_INSTANT_POPUP = _enum(QToolButton, 'ToolButtonPopupMode', 'InstantPopup', 'InstantPopup')
QT_LAYOUT_SET_DEFAULT_CONSTRAINT = _enum(QLayout, 'SizeConstraint', 'SetDefaultConstraint', 'SetDefaultConstraint')

QT_NETWORK_REPLY_NO_ERROR = _enum(QNetworkReply, 'NetworkError', 'NoError', 'NoError')
QGS_BLOCKING_NETWORK_NO_ERROR = _blocking_network_error('NoError')

QGIS_CRITICAL = _qgis_enum('MessageLevel', 'Critical')
QGIS_INFO = _qgis_enum('MessageLevel', 'Info')
QGIS_SUCCESS = _qgis_enum('MessageLevel', 'Success')
QGIS_WARNING = _qgis_enum('MessageLevel', 'Warning')

QGS_DISTANCE_DEGREES = _unit('Degrees', 'DistanceDegrees')
QGS_DISTANCE_KILOMETERS = _unit('Kilometers', 'DistanceKilometers')
QGS_DISTANCE_METERS = _unit('Meters', 'DistanceMeters')

QGS_TEMPORAL_MODE_FEATURE_DATE_TIME_INSTANT_FROM_FIELD = _temporal_mode(
    'ModeFeatureDateTimeInstantFromField',
    'ModeFeatureDateTimeInstantFromField'
)


def qt_user_role(offset=0):
    """Return Qt.UserRole plus an optional offset as an integer role value."""
    return QT_USER_ROLE + offset


def set_request_follow_redirects(request):
    """Set an explicit redirect policy on QNetworkRequest for Qt5 and Qt6."""
    try:
        request.setAttribute(
            QNetworkRequest.Attribute.RedirectPolicyAttribute,
            QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy,
        )
    except AttributeError:
        request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)


def qt_exec(dialog):
    """Execute a dialog in PyQt5/PyQt6 without relying on exec_()."""
    if hasattr(dialog, 'exec'):
        return dialog.exec()
    return dialog.exec_()
