from PySide2 import QtCore
import re
from PySide2.QtCore import Qt
from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from binaryninja import *

class Highlighter(QSyntaxHighlighter):
    def __init__(self,doc,selected,args):
        super(Highlighter,self).__init__(doc)
        self.selected = selected
        self.args = args

    def highlightBlock(self, text):
        # Highlight keywords
        keywords = ["^ +\\w+ (?=[*&_A-Za-z0-9\\[\\]]+;)","^\w+","\\bin_addr\\b","\\bssize_t\\b","\\bsocklen_t\\b","\\bsa_family_t\\b","\\b__int32_t\\b","\\b__int8_t\\b","\\b__int16_t\\b","\\b__uint32_t\\b","\\b__uint8_t\\b","\\b__uint16_t\\b","\\bpid_t\\b","\\bcode\\b","\\bLPSTR\\b","\\bSIZE_T\\b","\\bLPVOID\\b","\\bDWORD\\b","\\bclock_t\\b","\\bthis\\b","\\bUINT\\b","\\bHANDLE\\b","\\blonglong\\b","\\bushort\\b","\\bFILE\\b","\\bulong\\b","\\bbyte\\b","\\bfalse\\b","\\btrue\\b","\\buint\\b","\\bsize_t\\b","\\bundefined\\d*\\b","\\bchar\\b", "\\bclass\\b", "\\bconst\\b", "\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b","\\bfriend\\b", "\\binline\\b", "\\bint\\b","\\blong\\b", "\\bnamespace\\b", "\\boperator\\b","\\bprivate\\b", "\\bprotected\\b", "\\bpublic\\b","\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b","\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b","\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b","\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b","\\bvoid\\b", "\\bvolatile\\b", "\\bbool\\b"]
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor.fromRgb(62,156,202))
        for keyword in keywords:
            for match in re.finditer(keyword, text):
                self.setFormat(match.start(), match.end() - match.start(), keyword_format)
        # Highlight flow words
        flow_words = ["\\breturn\\b","\\bif\\b","\\belse\\b","\\bswitch\\b","\\bcase\\b","\\bwhile\\b","\\bfor\\b","\\bdo\\b","\\bgoto\\b"]
        flow_format = QTextCharFormat()
        flow_format.setForeground(QColor.fromRgb(197,134,192))
        for flow in flow_words:
            for match in re.finditer(flow, text):
                self.setFormat(match.start(), match.end() - match.start(), flow_format)
        # Highlight functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor.fromRgb(220,220,170))
        function_format.setForeground(QColor.fromRgb(253,216,53))
        function_pattern = "\\b\\w+(?=\\()"
        for match in re.finditer(function_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), function_format)
        # Highlight comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor.fromRgb(82,153,85))
        comment_pattern = "\/\/.*$"
        for match in re.finditer(comment_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), comment_format)
        multi_comment_pattern = "(?s)\\/\\*.*?\\*\\/"
        for match in re.finditer(multi_comment_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), comment_format)
        # Highlight string constants
        const_format = QTextCharFormat()
        const_format.setForeground(QColor.fromRgb(206,145,120))
        string_consts = "\"(.*?)\""
        for match in re.finditer(string_consts, text):
            self.setFormat(match.start(), match.end() - match.start(), const_format)
        # Highlight numeric constants
        num_const_format = QTextCharFormat()
        num_const_format.setForeground(QColor.fromRgb(139,195,74))
        num_consts = "\\b\\d+\\b"
        for match in re.finditer(num_consts, text):
            self.setFormat(match.start(), match.end() - match.start(), num_const_format)
        hex_const = "0x[0-9a-f]+\\b"
        for match in re.finditer(hex_const, text):
            self.setFormat(match.start(), match.end() - match.start(), num_const_format)
        # Highlight data
        data_format = QTextCharFormat()
        data_format.setForeground(QColor.fromRgb(142,230,237))
        data_consts = "\\b(PTR)?_?DAT_[0-9a-zA-Z]+\\b"
        for match in re.finditer(data_consts, text):
            self.setFormat(match.start(), match.end() - match.start(), data_format)
        # Highlight CPP Class paths
        cpp_format = QTextCharFormat()
        cpp_format.setForeground(QColor.fromRgb(142,230,237))
        cpp_path = "\\b\\w*(?=::)"
        for match in re.finditer(cpp_path, text):
            self.setFormat(match.start(), match.end() - match.start(), cpp_format)
        # Params
        params_format = QTextCharFormat()
        params_format.setForeground(QColor.fromRgb(128,216,255))
        for arg in self.args:
            params_pattern = "\\b" + arg + "\\b"
            for match in re.finditer(params_pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), params_format)
        # Highlight selection
        if self.selected:
            selection_format = QTextCharFormat()
            selection_format.setBackground(QColor.fromRgb(121,195,231))
            selection_format.setForeground(QColor.fromRgb(42,42,42))
            try:
                selection_pattern = self.selected
                for match in re.finditer(selection_pattern, text):
                    self.setFormat(match.start(), match.end() - match.start(), selection_format)
            except:
                pass
        
