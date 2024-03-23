import copy
import time
from ctypes import *
from array import *
import math
from enum import IntEnum
import json

u8 = c_uint8
u16 = c_uint16
u32 = c_uint32
u64 = c_uint64

U8 = c_uint8
U16 = c_uint16
U32 = c_uint32
U64 = c_uint64


class CTRL_DIR_376_2(IntEnum):
    E_DIR_DOWN = 0
    E_DIR_UP = 1


class CTRL_PRM_376_2(IntEnum):
    E_FRAME_FROM_SLAVE = 0
    E_FRAME_FROM_MASTER = 1


class CTRL_COMM_376_2(IntEnum):
    RESERVE = 0        # 保留
    CENTRALIZATION_ROUTE = 1        # 集中式路由
    DISTRIBUTED_ROUTE = 2        # 分布式路由
    HPLC_CARRIER = 3        # 宽带载波通信
    WIRELESS_COMM = 10       # 无线通信
    TCP_AND_IP_COMM = 20       # 以太网通信


class R_DOWN_RouterMode(IntEnum):
    ROUTE_MODE = 1        # 带路由模式
    NO_ROUTE_MODE = 0        # 不带路由模式


class R_DOWN_SubNodeFlag(IntEnum):
    NO_SUBJOIN_NODE = 0        # 无附加节点
    HAVE_SUBJOIN_NODE = 1        # 有附加节点


class R_DOWN_ComModuleFlag(IntEnum):
    CCO = 0        # 表示对主节点操作
    STA = 1        # 表示对从节点操作


class R_DOWN_CT(IntEnum):
    NO_CONFLICT = 0        # 不冲突
    CONFLICT = 1        # 冲突


class R_DOWN_RelayLevel(IntEnum):
    LAVEL0 = 0        # 中级级别0
    LAVEL1 = 1        # 中级级别1
    LAVEL2 = 2        # 中级级别2
    LAVEL3 = 3        # 中级级别3
    LAVEL4 = 4        # 中级级别4
    LAVEL5 = 5        # 中级级别5
    LAVEL6 = 6        # 中级级别6
    LAVEL7 = 7        # 中级级别7
    LAVEL8 = 8        # 中级级别8
    LAVEL9 = 9        # 中级级别9
    LAVEL10 = 10       # 中级级别10
    LAVEL11 = 11       # 中级级别11
    LAVEL12 = 12       # 中级级别12
    LAVEL13 = 13       # 中级级别13
    LAVEL14 = 14       # 中级级别14
    LAVEL15 = 15       # 中级级别15


class R_DOWN_ChannelID(IntEnum):
    CHANNEL0 = 0  # 不区分信道
    CHANNEL1 = 1  # 信道标识1
    CHANNEL2 = 2  # 信道标识2
    CHANNEL3 = 3  # 信道标识3
    CHANNEL4 = 4  # 信道标识4
    CHANNEL5 = 5  # 信道标识5
    CHANNEL6 = 6  # 信道标识6
    CHANNEL7 = 7  # 信道标识7
    CHANNEL8 = 8  # 信道标识8
    CHANNEL9 = 9  # 信道标识9
    CHANNEL10 = 10  # 信道标识10
    CHANNEL11 = 11  # 信道标识11
    CHANNEL12 = 12  # 信道标识12
    CHANNEL13 = 13  # 信道标识13
    CHANNEL14 = 14  # 信道标识14
    CHANNEL15 = 15  # 信道标识15


class R_DOWN_ErrBate(IntEnum):
    NO_CODING = 0  # 未编码
    RS_CODING = 1  # RS编码
    RESEVER = 2    # 保留


class R_DOWN_AnswerBytes(IntEnum):
    ELSE_TIME = 1
    DEFAULT_TIME = 0  # 延迟等待时间为默认时间


# 通信协议类型定义
class COMM_PROTOCOL(IntEnum):
    dlt645_97 = 1  # DLT645——1997
    dlt645_07 = 2  # DLT645-2007
    dlt698_45 = 3  # DLT698-45

# 控制字类型定义


class CONTROL(IntEnum):
    transparent = 0  # 透明传输
    dlt645_97 = 1  # DLT645——1997
    dlt645_07 = 2  # DLT645-2007
    Phase_id = 3  # 相位识别功能


# 20210316
# //报文控制字
class GW376_2_Ctrl(Structure):
    _pack_ = 1
    _fields_ = [("bComm", u8, 6),  # // 通信方式
                ("bPrm", u8, 1),  # // 启动标识 0: 报文来自从动站  1: 报文来自启动站
                ("bDir", u8, 1)]  # // 传输方向 0: 下行 集中器发出 1: 上行 模块发出


# //信息域下行结构
class GW376_2_R_DOWN(Structure):
    _pack_ = 1
    _fields_ = [("bRouterMode", u8, 1),  # //路由标识
                ("bSubNodeFlag", u8, 1),  # //附属节点标识
                ("bComModuleFlag", u8, 1),  # //通信模块标识
                ("bCT", u8, 1),  # //冲突检测
                ("bRelayLevel", u8, 4),  # //中级级别

                ("bChannelID", u8, 4),  # //信道标识
                ("bErrBate", u8, 4),  # //纠错编码标识

                ("ucAnswerBytes", u8),  # //预计应答字节数

                ("bCommSpeed", u16, 15),  # //通信速率
                ("bErrBate", u16, 1),  # //速率单位标识

                ("ucFrameSn", u8)]  # //帧序号


# //信息域上行结构
class GW376_2_R_UP(Structure):
    _pack_ = 1
    _fields_ = [("bRouterMode", u8, 1),  # //路由标识
                ("bReserveB0b1", u8, 1),  #
                ("bComModuleFlag", u8, 1),  # //通信模块标识
                ("bReserveB0b3", u8, 1),  #
                ("bRelayLevel", u8, 4),  # //中级级别

                ("bChannelID", u8, 4),  # //信道标识
                ("bReserveB1b4_7", u8, 4),  #

                ("bRealPhaseID", u8, 4),  # //实测相位
                ("bMeterCommAttr", u8, 4),  # //电能表通道特征

                ("bSignalQvofCmd", u8, 4),  # //末级命令信号品质
                ("bErrBate", u8, 4),  # //末级应答信号品质

                ("bEventFlag", u8, 1),  # //事件标志
                ("bLineFlag", u8, 1),  # //线路标识_0表示归属无异常 1表示归属有异常
                ("bArea", u8, 3),  # //台区状态_0表示归属无异常 1表示归属有异常
                ("bReserveB4b1_7", u8, 3),  #

                ("ucFrameSn", u8)]  # //帧序号


# 1376.2数据帧格式
class sApsCommonStructD(Structure):
    _pack_ = 1
    _fields_ = [("Head", u8),  # //报文端口号
                ("Len", u16),  # //报文ID
                ("GW376_Ctrl", GW376_2_Ctrl),  # //报文控制字
                ("GW376_R_DOWN", GW376_2_R_DOWN)]  # //报文控制字


# 1376.2数据帧格式
class sApsCommonStructU(Structure):
    _pack_ = 1
    _fields_ = [("Head", u8),  # //报文端口号
                ("Len", u16),  # //报文ID
                ("GW376_Ctrl", GW376_2_Ctrl),  # //报文控制字
                ("GW376_R_UP", GW376_2_R_UP)]  # //报文控制字


# 1376.2数据帧格式
class s376_2UpDowm(Union):
    _pack_ = 1
    _fields_ = [("dowm", GW376_2_R_DOWN),  # // 信息域下行
                ("up", GW376_2_R_UP)]  # // 信息域上行

# 数据帧格式


class s376_2(Structure):
    _pack_ = 1
    _fields_ = [("head", u8),  # // 头0x68
                ("len", u16),  # // 报文长度
                ("ctrl", GW376_2_Ctrl),  # // 报文控制字
                ("info", s376_2UpDowm),  # // 信息域
                ("buff", (u8 * 2))]  # // cs 0x16

# 地址格式


class sAddr(Structure):
    _pack_ = 1
    _fields_ = [("addr", (u8 * 6))]  # // 地址格式定义


class DT(Structure):
    _pack_ = 1
    _fields_ = [("DT1", u8),  # // 数据单元标识DT1
                ("DT2", u8)]  # // 数据单元标识DT2


class appData(Structure):
    _pack_ = 1
    _fields_ = [("AFN", u8),  # // 应用功能AFN
                ("Fn", DT)]  # // 数据单元标识=Fn DT1在前，DT2在后
    # ("appDataLen",              u16)]               # // 数据单单元长度


class s376_2RecvInfo(Structure):
    _pack_ = 1
    _fields_ = [("ctrl", GW376_2_Ctrl),  # // 报文控制字
                ("dowmInfo", GW376_2_R_DOWN),  # // 信息域下行
                ("upInfo", GW376_2_R_UP),  # // 信息域上行
                ("srcAddr_A1", (u8 * 6)),  # // 源地址A1
                ("relayAddr_A2", (sAddr * 15)),  # // 中继地址A2
                ("dstAddr_A3", (u8 * 6)),  # // 目的地址A3
                ("AFN", u8),  # // 应用功能AFN
                ("Fn", u16),  # // 数据单元标识
                ("DT", u16),  # // 数据单元标识=Fn DT1在前，DT2在后
                ("DT1", u8),  # // 数据单元标识DT1
                ("DT2", u8),  # // 数据单元标识DT2
                ("appDataLen", u16),  # // 应用数据长度
                ("pAppData", POINTER(u8))]  # // 数据单元


#   确认帧
class AFN00Fn01(Structure):
    _pack_ = 1
    _fields_ = [("D0", u8, 1),  # // 信道00状态 0：忙 1：闲
                ("D1", u8, 1),  # // 信道01状态 0：忙 1：闲
                ("D2", u8, 1),  # // 信道02状态 0：忙 1：闲
                ("D3", u8, 1),  # // 信道03状态 0：忙 1：闲
                ("D4", u8, 1),  # // 信道04状态 0：忙 1：闲
                ("D5", u8, 1),  # // 信道05状态 0：忙 1：闲
                ("D6", u8, 1),  # // 信道06状态 0：忙 1：闲
                ("D7", u8, 1),  # // 信道07状态 0：忙 1：闲
                ("D8", u8, 1),  # // 信道08状态 0：忙 1：闲
                ("D9", u8, 1),  # // 信道09状态 0：忙 1：闲
                ("D10", u8, 1),  # // 信道10状态 0：忙 1：闲
                ("D11", u8, 1),  # // 信道11状态 0：忙 1：闲
                ("D12", u8, 1),  # // 信道12状态 0：忙 1：闲
                ("D13", u8, 1),  # // 信道13状态 0：忙 1：闲
                ("D14", u8, 1),  # // 信道14状态 0：忙 1：闲
                ("D15", u8, 1),  # // 信道15状态 0：忙 1：闲
                ("waterTime", u16)]  # // 等待时间单位 s


class AFN02Fn01(Structure):
    _pack_ = 1
    _fields_ = [("commProtocol", u8),  # // 通信协议
                ("appDataLen", u8)]    # // 报文长度


class AFNF0Fn203(Structure):
    _pack_ = 1
    _fields_ = [("commProtocol", u8)  # // 通信协议
                ]


class AFN11Fn04_WORK_MODE(Structure):
    _pack_ = 1
    _fields_ = [("working_condition", u8, 1),  # // 工作状态
                ("allow_status",  u8, 1),     # // 允许状态
                ("nbackup", u8, 2),           # // 备用
                ("Error_Correction", u8, 4),  # // 纠错编码
                ("comm_speed", u16, 15),     # // 通信速率
                ("units", u16, 1)               # // 速率单位标识
                ]


class GW376_2Base(object):
    def __init__(self, ifcfun=None, myPrint=print, localFun=None, c_base=None, ttbase=None):
        self.ifcfun = ifcfun
        self.myPrint = myPrint
        self.localFun = localFun
        self.c_base = c_base
        self.ttbase = ttbase
        self.Recv376_2Info = s376_2RecvInfo()
        self.Recv376_2Userdata = None
        self.sendBuff = (u8 * 2000)()
        self.m_offset = 0
        self.CCO_MAC = (u8 * 6)(0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        self.STA_MAC = (u8 * 6)(0x05, 0x12, 0x88, 0x06, 0x00, 0x00)
        self.iAFN = 0x00  # 输入的功能码
        self.iFn = 0  # 输入的Fn

    def setCCO_MAC(self, mac=''):
        if len(mac) == 12:
            mac_2_bytes = bytes.fromhex(mac)
            self.CCO_MAC = (u8 * 6)(mac_2_bytes[5], mac_2_bytes[4],
                                    mac_2_bytes[3], mac_2_bytes[2], mac_2_bytes[1], mac_2_bytes[0])
        else:
            return '设置CCO_MAC失败'

    def setSTA_MAC(self, mac=''):
        if len(mac) == 12:
            mac_2_bytes = bytes.fromhex(mac)
            self.STA_MAC = (u8 * 6)(mac_2_bytes[5], mac_2_bytes[4],
                                    mac_2_bytes[3], mac_2_bytes[2], mac_2_bytes[1], mac_2_bytes[0])
        else:
            return '设置STA_MAC失败'

    def Check_376_2_Frame(self, DataLen, DataBuf, CheckDI1, CheckDI2, CheckDI3):
        try:
            if (DataLen.value < 4):
                return False
            ApsCommonStructD = addressof(
                cast(DataBuf, POINTER(sApsCommonStructD)).contents)

            # self.myPrint('ApsCommonStructD = {}'.format(DataBuf[0]))
            if (DataBuf[0] != 0x68):
                return False
            # self.myPrint('ApsCommonStructD = {}'.format(DataBuf[DataLen.value - 1]))
            if (DataBuf[DataLen.value - 1] != 0x16):
                return False
            Check_Sum = 0
            for i in range(DataLen.value - 5):
                Check_Sum += DataBuf[i + 3]
            # self.myPrint('Check_Sum    :{}'.format(Check_Sum))
            Sum = (c_ubyte * 2)()
            Sum[0] = Check_Sum
            # self.myPrint('Check_Sum = {} {}'.format(Sum[0],DataBuf[DataLen.value - 2]))
            if (Sum[0] == DataBuf[DataLen.value - 2]):
                # self.myPrint('Check_Sum = {} {} {}'.format(DataBuf[10], DataBuf[11], DataBuf[12]))
                # self.myPrint('Check_Sum = {} {} {}'.format(CheckDI1, CheckDI2, CheckDI3))
                if CheckDI1 == DataBuf[10] and CheckDI2 == DataBuf[11] and CheckDI3 == DataBuf[12]:
                    return True
        except Exception as e:
            self.myPrint('Check_376_2_Frame Err:{}'.format(e.args))
        return False

    def Chk376_2Frame(self, pData: POINTER(u8), dataLen: int):
        if (dataLen < sizeof(s376_2)):
            return 1

        pBuf = cast(pData, POINTER(u8))
        f376_2 = cast(pData, POINTER(s376_2)).contents
        if (f376_2.head != 0x68) or (dataLen < f376_2.len):
            return 2

        if (None != self.c_base):
            cs = self.c_base.HplcAndRfBase.Nwk_GetChkSum(pBuf, dataLen - 2)
            if (cs != pBuf[dataLen - 2]):
                return 3

        return 0

    # @classmethod
    def get376_2Info(self, pData, dataLen):
        if (self.Chk376_2Frame(pData, dataLen)):
            return 1
        pBuf = cast(pData, POINTER(u8))
        addr = addressof(pData)
        offset = 0
        self.Recv376_2Info = s376_2RecvInfo()
        f376_2 = cast(pData, POINTER(s376_2)).contents
        try:
            self.Recv376_2Info.ctrl = f376_2.ctrl
            self.Recv376_2Info.dowmInfo = f376_2.info.dowm
            self.Recv376_2Info.upInfo = f376_2.info.up
            self.Recv376_2Info.ctrl = f376_2.ctrl

            offset += sizeof(s376_2) - sizeof(f376_2.buff)
            if (f376_2.info.dowm.bComModuleFlag > 0):
                memmove(self.Recv376_2Info.srcAddr_A1,
                        addr + offset, sizeof(sAddr))
                memmove(self.Recv376_2Info.relayAddr_A2, addr + offset + sizeof(sAddr),
                        sizeof(sAddr) * f376_2.info.dowm.bRelayLevel)
                memmove(self.Recv376_2Info.dstAddr_A3,
                        addr + offset + (f376_2.info.dowm.bRelayLevel + 1) * sizeof(sAddr), sizeof(sAddr))
                offset += (f376_2.info.dowm.bRelayLevel + 2) * sizeof(sAddr)

            self.Recv376_2Info.AFN = pBuf[offset]
            offset += 1
            self.Recv376_2Info.DT = (pBuf[offset + 1] << 8) + pBuf[offset]
            self.Recv376_2Info.DT1 = pBuf[offset]
            self.Recv376_2Info.DT2 = pBuf[offset + 1]
            if (self.Recv376_2Info.DT1 > 0):
                # tmp = int(math.log2(pBuf[offset]))
                self.Recv376_2Info.Fn = (
                    self.Recv376_2Info.DT2 * 8) + int(math.log2(self.Recv376_2Info.DT1)) + 1
            else:
                self.Recv376_2Info.Fn = 0
            offset += 2

            self.Recv376_2Info.appDataLen = f376_2.len - \
                offset - sizeof(f376_2.buff)
            self.Recv376_2Info.pAppData = cast(addr + offset, POINTER(u8))
            if self.Recv376_2Info.AFN == 0x00:
                if self.Recv376_2Info.Fn == 1:
                    print('appdata=',)
                elif self.Recv376_2Info.Fn == 2:
                    print('否认帧被找到')
            elif self.Recv376_2Info.AFN == 0x01:
                if self.Recv376_2Info.Fn == 1:
                    print('appdata=')
                elif self.Recv376_2Info.Fn == 2:
                    print('否认帧被找到')
            elif self.Recv376_2Info.AFN == 0xf0:
                if self.Recv376_2Info.Fn == 203:
                    self.decodeAppData = (u8 * self.Recv376_2Info.appDataLen)()
                    self.Recv376_2Userdata = AFNF0Fn203()
                    self.Recv376_2Userdata.commProtocol = self.Recv376_2Info.pAppData[0]
                    for i in range(self.Recv376_2Info.appDataLen):
                        self.decodeAppData[i] = self.Recv376_2Info.pAppData[i]
            else:
                print('AFN索引解析未增加')
            self.decodeAppData = (u8 * self.Recv376_2Info.appDataLen)()
            for i in range(self.Recv376_2Info.appDataLen):
                self.decodeAppData[i] = self.Recv376_2Info.pAppData[i]
            temp = self.byte_arr2hex(
                self.decodeAppData, '', rlen=self.Recv376_2Info.appDataLen)

            print({
                'Start Char': '{:02x}'.format(0x68),
                'Length': '{:d}'.format(dataLen),
                # '帧控制': '{:02x}'.format(self.Recv376_2Info.ctrl),
                'Frame Control':
                    {'bDir': '{:d}'.format(self.Recv376_2Info.ctrl.bDir),
                     'bPrm': '{:d}'.format(self.Recv376_2Info.ctrl.bPrm),
                     'bComm': '{:d}'.format(self.Recv376_2Info.ctrl.bComm),
                     },
                # '信息域': '{:s*8}'.format(self.Recv376_2Info.upInfo),
                'Information Field':
                    {'Route Idenctification': '{:d}'.format(self.Recv376_2Info.upInfo.bRouterMode),
                     'B0': '{:d}'.format(self.Recv376_2Info.upInfo.bReserveB0b1),
                     'Communication Module Identif': '{:02x}'.format(self.Recv376_2Info.upInfo.bComModuleFlag),
                     'B3': '{:d}'.format(self.Recv376_2Info.upInfo.bReserveB0b3),
                     'Inrtermediate level': '{:d}'.format(self.Recv376_2Info.upInfo.bRelayLevel),
                     'Chnaennel ': '{:d}'.format(self.Recv376_2Info.upInfo.bChannelID),
                     'B1b4_7': '{:d}'.format(self.Recv376_2Info.upInfo.bReserveB1b4_7),
                     'Measuren Phase': '{:d}'.format(self.Recv376_2Info.upInfo.bRealPhaseID),
                     'Energy meter channel char': '{:d}'.format(self.Recv376_2Info.upInfo.bMeterCommAttr),
                     'last level commandt': '{:d}'.format(self.Recv376_2Info.upInfo.bSignalQvofCmd),
                     'u': '{:d}'.format(self.Recv376_2Info.upInfo.bErrBate),
                     'lineLoss Petualangan hebat kan': '{:d}'.format(self.Recv376_2Info.upInfo.bEventFlag),
                     '线路标识_0表示归属无异常 1表示归属有异常': '{:d}'.format(self.Recv376_2Info.upInfo.bLineFlag),
                     '台区状态_0表示归属无异常 1表示归属有异常': '{:d}'.format(self.Recv376_2Info.upInfo.bArea),
                     'B4b1_7': '{:d}'.format(self.Recv376_2Info.upInfo.bReserveB4b1_7),
                     },
                'AFN': '{:02x}'.format(self.Recv376_2Info.AFN),
                'Fn': '{:d}'.format(self.Recv376_2Info.Fn),
                '应用数据': temp
            })

        except Exception as e:
            self.myPrint('py UpholdPeriod Err:{}'.format(e.args))

        return 0

    def make376_2frame(self, sMAC=None, dMAC=None, bComModuleFlag=None, ucFrameSn=None, user_data=None):
        m3762frame = s376_2()
        m3762frame.head = 0x68  # 起始符
        m3762frame.len = 00  # 帧长
        m3762frame.ctrl.bComm = 3  # 通信方式
        m3762frame.ctrl.bPrm = 1  # 启动标识位
        m3762frame.ctrl.bDir = 0  # 传输方向
        m3762frame.info.dowm.bRouterMode = 0  # 路由标识
        m3762frame.info.dowm.bSubNodeFlag = 0  # 附属节点标识
        m3762frame.info.dowm.bComModuleFlag = bComModuleFlag  # 通信模块标识
        m3762frame.info.dowm.bCT = 0  # 冲突检测
        m3762frame.info.dowm.bRelayLevel = 0  # 中继级别
        m3762frame.info.dowm.bChannelID = 0  # 信道标识
        m3762frame.info.dowm.bErrBate = 0  # 纠错编码标识
        m3762frame.info.dowm.ucAnswerBytes = 1  # 预计应答字节数
        m3762frame.info.dowm.bCommSpeed = 0  # 通信速率
        m3762frame.info.dowm.bErrBate = 0  # 速率单位标识
        m3762frame.info.dowm.ucFrameSn = ucFrameSn  # 报文序列号
        saddr = sMAC
        daddr = dMAC
        appdata = appData()
        appdata.AFN = self.iAFN
        Dt1_list = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
        fn = self.iFn
        if fn % 8 != 0:
            dt2 = (fn // 8)
            dt1 = Dt1_list[(fn % 8) - 1]
        else:
            dt2 = (fn // 8) - 1
            dt1 = Dt1_list[-1]
        appdata.Fn.DT1 = dt1
        appdata.Fn.DT2 = dt2
        memmove(addressof(self.sendBuff) + self.m_offset,
                addressof(m3762frame), sizeof(m3762frame) - 2)
        self.m_offset = self.m_offset + sizeof(m3762frame) - 2
        if m3762frame.info.dowm.bComModuleFlag == 1:
            memmove(addressof(self.sendBuff) + self.m_offset,
                    addressof(saddr), sizeof(sAddr))
            self.m_offset = self.m_offset + sizeof(sAddr)
            memmove(addressof(self.sendBuff) + self.m_offset,
                    addressof(daddr), sizeof(sAddr))
            self.m_offset = self.m_offset + sizeof(sAddr)
        else:
            pass
        memmove(addressof(self.sendBuff) + self.m_offset,
                addressof(appdata), sizeof(appdata))
        self.m_offset = self.m_offset + sizeof(appdata)
        memmove(addressof(self.sendBuff) + self.m_offset,
                addressof(user_data), sizeof(user_data))
        self.m_offset = self.m_offset + sizeof(user_data)
        self.packCs()
        self.packFramelen()
        return self.sendBuff[0:self.m_offset + 1], self.m_offset

    def clear(self):
        self.m_offset = 0
        self.sendBuff = (u8 * 2000)()

    def packCs(self):
        p_frame = cast(pointer(self.sendBuff), POINTER(c_uint8))
        cs = 0
        for i in range(3, self.m_offset, 1):
            cs = cs + p_frame[i]
            # print('参与计算的值{:02x}'.format(p_frame[i]))
        End = (u8 * 2)(cs, 0x16)
        memmove(addressof(self.sendBuff) + self.m_offset, addressof(End), 2)
        self.m_offset = self.m_offset + 2

    def packFramelen(self):
        m3762frame_len = (u16 * 1)(self.m_offset)
        memmove(addressof(self.sendBuff) + 1, addressof(m3762frame_len), 2)

# 确认帧，无数据域
    def packAppdata_AFN00Fn01(self, channelstatus=None, m_time=None):
        self.iAFN = 0x00  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        out_appdata = (u8 * 4)()
        out_appdata[0:2] = channelstatus & 0xff, channelstatus >> 8
        out_appdata[2:4] = m_time & 0xff, m_time >> 8
        return out_appdata

# 否认帧，无数据域
    def packAppdata_AFN00Fn02(self, err=None):
        self.iAFN = 0x00  # 输入的功能码
        self.iFn = 2  # 输入的Fn
        out_appdata = (u8 * 1)(err)
        return out_appdata

 # 硬件初始化，无数据域
    def packAppdata_AFN01Fn01(self):
        self.iAFN = 0x01  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

 # 参数初始化，无数据域
    def packAppdata_AFN01Fn02(self):
        self.iAFN = 0x01  # 输入的功能码
        self.iFn = 2  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

 # 数据初始化，无数据域
    def packAppdata_AFN01Fn03(self):
        self.iAFN = 0x01  # 输入的功能码
        self.iFn = 3  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

 # 数据转发，转发通信协议数据帧
    def packAppdata_AFN02Fn01(self, comm_protocol_type=None, message_len=None, message=None):
        self.iAFN = 0x02  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        out_appdata = (u8 * (message_len + 2))(comm_protocol_type, message_len)
        memmove(addressof(out_appdata)+2, addressof(message), sizeof(message))
        return out_appdata

# 查询模块厂商版本信息，带地址的则是查询从节点版本信息，无数据域
    def packAppdata_AFN03Fn01(self):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

 # 噪声值，无数据单元
    def packAppdata_AFN03Fn02(self):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 2  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

 # 从节点侦听信息
    def packAppdata_AFN03Fn03(self, start=None, nodenum=None):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 3  # 输入的Fn
        # start:开始节点指针  从0开始 0为主节点    nodenum:读取节点数量 <=16
        out_appdata = (u8 * 2)(start, nodenum)
        return out_appdata

 # 查询主节点地址，无数据域
    def packAppdata_AFN03Fn04(self):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 4  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

# 查询主节点状态字和通信速率，无数据域
    def packAppdata_AFN03Fn05(self):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 5  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

# 查询主节点干扰状态
    def packAppdata_AFN03Fn06(self, m_time=None):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 6  # 输入的Fn
        out_appdata = (u8 * 1)(m_time)    # m_time:持续时间 单位 min
        return out_appdata

 # 读取从节点监控最大超时时间，无数据域
    def packAppdata_AFN03Fn07(self):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 7  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

 # 查询无线通信参数，无数据域
    def packAppdata_AFN03Fn08(self):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 8  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

# 通信延时相关广播通信时长
    def packAppdata_AFN03Fn09(self, comm_protocol_type=None, message_len=None, message=None):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 9  # 输入的Fn
        # comm_protocol_type 通信协议类型   00：透明传输 01：645-1997 02：645-2007 03：698.45
        # message_len 报文长度
        out_appdata = (u8 * (message_len+2))(comm_protocol_type, message_len)
        memmove(addressof(out_appdata)+2, addressof(message), sizeof(message))
        return out_appdata

# 查询本地通信模块运行模式，无数据域
    def packAppdata_AFN03Fn10(self):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 10  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

 # 查询本地通信模块AFN索引
    def packAppdata_AFN03Fn11(self, AFN=None):
        self.iAFN = 0x03  # 输入的功能码
        self.iFn = 11     # 输入的Fn
        # AFN功能码
        out_appdata = (u8 * 1)(AFN)
        memmove(addressof(self.sendBuff) + self.m_offset,
                addressof(out_appdata), sizeof(out_appdata))
        self.m_offset = self.m_offset + sizeof(out_appdata)
        return out_appdata

# 发送测试
    def packAppdata_AFN04Fn01(self, m_time=None):
        self.iAFN = 0x04  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        # m_time 持续时间  0：表示停止发送  单位 s
        out_appdata = (u8 * 1)(m_time)
        memmove(addressof(self.sendBuff) + self.m_offset,
                addressof(out_appdata), sizeof(out_appdata))
        self.m_offset = self.m_offset + sizeof(out_appdata)
        return out_appdata

# 从节点点名，无数据域
    def packAppdata_AFN04Fn02(self):
        self.iAFN = 0x04  # 输入的功能码
        self.iFn = 2  # 输入的Fn
        out_appdata = (u8 * 0)()
        return out_appdata

# 本地通信模块报文通信测试
    def packAppdata_AFN04Fn03(self, testcommspeed=None, daddr=None, comm_protocol_type=None, message_len=None, message=None):
        self.iAFN = 0x04  # 输入的功能码
        self.iFn = 3  # 输入的Fn
        out_appdata = (u8 * (message_len+9))()
        out_appdata[0] = testcommspeed
        memmove(addressof(out_appdata) + 1, addressof(daddr), 6)
        out_appdata[7:9] = comm_protocol_type, message_len
        memmove(addressof(out_appdata) + 9,
                addressof(message), sizeof(message))
        return out_appdata

 # 设置主节点地址
    def packAppdata_AFN05Fn01(self, setCCO_MAC=None):
        self.iAFN = 0x05  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        out_appdata = setCCO_MAC
        return out_appdata

# 允许/禁止从节点主动上报
    def packAppdata_AFN05Fn02(self,  allow_or_forbid=None):
        # allow_or_forbid 事件上报状态标识 1：允许  2：禁止
        self.iAFN = 0x05  # 输入的功能码
        self.iFn = 2      # 输入的Fn
        out_appdata = (u8*1)(allow_or_forbid)
        return out_appdata

# 启动广播
    def packAppdata_AFN05Fn03(self,  control=None, message_len=None, message=None):
        self.iAFN = 0x05  # 输入的功能码
        self.iFn = 3  # 输入的Fn
        # control: 控制字  协议类型
        # message_len: 报文长度
        out_appdata = (u8*(message_len+2))()
        offset = 0
        out_appdata[0:2] = control, message_len
        offset += 2
        memmove(addressof(out_appdata) + offset,
                addressof(message), message_len)
        offset += message_len
        return out_appdata

# 设置从节点监控最大超时时间
    def packAppdata_AFN05Fn04(self, maxtimeout=None):
        self.iAFN = 0x05  # 输入的功能码
        self.iFn = 4  # 输入的Fn
        # maxtimeout:最大超时时间单位 s
        out_appdata = (u8*1)()
        offset = 0
        out_appdata[0] = maxtimeout
        offset += 1
        return out_appdata

# 查询从节点数量，无数据单元
    def packAppdata_AFN10Fn01(self):
        self.iAFN = 0x10  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        out_appdata = (u8*0)()
        return out_appdata

# 查询从节点信息
    def packAppdata_AFN10Fn02(self, Initial_sequence: int, number: int):
        self.iAFN = 0x10  # 输入的功能码
        self.iFn = 2  # 输入的Fn
        # Initial_sequence:起始序列号2bytes
        # number: 从节点数量1byte
        out_appdata = (u8*3)()
        seq = (U16*1)(Initial_sequence)
        memmove(addressof(out_appdata), addressof(seq), 2)
        out_appdata[2] = number
        return out_appdata

# 指定从节点的上一级中继路由信息
    def packAppdata_AFN10Fn03(self, Slave_node_addr: str):
        self.iAFN = 0x10  # 输入的功能码
        self.iFn = 3  # 输入的Fn
        # Slave_node_addr : 从节点地址
        addrs_bytes = bytes.fromhex(Slave_node_addr)
        m_address = (u8 * len(addrs_bytes)).from_buffer_copy(addrs_bytes)
        out_appdata = (u8*6)()
        memmove(addressof(out_appdata), addressof(m_address), 6)
        return out_appdata

# 查询路由运行状态，无数据单元
    def packAppdata_AFN10Fn04(self):
        self.iAFN = 0x10  # 输入的功能码
        self.iFn = 4  # 输入的Fn2
        out_appdata = (u8*0)()
        return out_appdata

# 未抄读成功的从节点信息
    def packAppdata_AFN10Fn05(self, Initial_sequence: int, number: int):
        self.iAFN = 0x10  # 输入的功能码
        self.iFn = 5  # 输入的Fn
        # Initial_sequence:起始序列号2bytes
        # number: 从节点数量1byte
        out_appdata = (u8*3)()
        seq = (U16*1)(Initial_sequence)
        memmove(addressof(out_appdata), addressof(seq), 2)
        out_appdata[2] = number
        return out_appdata

# 主动注册的从节点信息
    def packAppdata_AFN10Fn06(self, Initial_sequence: int, number: int):
        self.iAFN = 0x10  # 输入的功能码
        self.iFn = 6  # 输入的Fn
        # Initial_sequence:起始序列号2bytes
        # number: 从节点数量1byte
        out_appdata = (u8*3)()
        seq = (U16*1)(Initial_sequence)
        memmove(addressof(out_appdata), addressof(seq), 2)
        out_appdata[2] = number
        return out_appdata

# 添加从节点
    def packAppdata_AFN11Fn01(self, number: int, addrs_list: list):
        self.iAFN = 0x11  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        # number: 从节点数量1byte
        # addrs_list:从节点地址列表[['051288060000',2],['061288060000',3]]7bytes
        out_appdata = (u8*((number*7)+1))()
        offset = 0
        out_appdata[0] = number
        offset += 1
        for index in addrs_list:
            addrs_bytes = bytes.fromhex(index[0])
            m_address = (u8 * len(addrs_bytes)).from_buffer_copy(addrs_bytes)
            memmove(addressof(out_appdata)+offset, addressof(m_address), 6)
            offset += 6
            out_appdata[offset] = index[1]
            offset += 1
        return out_appdata

# 删除从节点
    def packAppdata_AFN11Fn02(self, number: int, addrs_list: list):
        self.iAFN = 0x11  # 输入的功能码
        self.iFn = 2  # 输入的Fn
        # number: 从节点数量1byte
        # addrs_list:从节点地址列表['051288060000','061288060000']6bytes
        out_appdata = (u8*((number*6)+1))()
        offset = 0
        out_appdata[0] = number
        offset += 1
        for index in addrs_list:
            addrs_bytes = bytes.fromhex(index)
            m_address = (u8 * len(addrs_bytes)).from_buffer_copy(addrs_bytes)
            memmove(addressof(out_appdata)+offset, addressof(m_address), 6)
            offset += 6
        return out_appdata

# 设置从节点固定中继路径
    def packAppdata_AFN11Fn03(self, Slave_node_addr: str, RelayLevel: int, addrs_list: list):
        self.iAFN = 0x11  # 输入的功能码
        self.iFn = 3  # 输入的Fn
        # Slave_node_addr: 从节点地址6bytes
        # RelayLevel: 中继级别1byte
        # addrs_list: 中继地址列表['051288060000','061288060000']6bytes
        out_appdata = (u8*((RelayLevel*6)+7))()
        offset = 0
        Slave_node_addr_bytes = bytes.fromhex(Slave_node_addr)
        m_address = (u8 * len(Slave_node_addr_bytes)
                     ).from_buffer_copy(Slave_node_addr_bytes)
        memmove(addressof(out_appdata)+offset, addressof(m_address), 6)
        offset += 6
        out_appdata[offset] = RelayLevel
        offset += 1
        for index in addrs_list:
            addrs_bytes = bytes.fromhex(index)
            m_address = (u8 * len(addrs_bytes)).from_buffer_copy(addrs_bytes)
            memmove(addressof(out_appdata)+offset, addressof(m_address), 6)
            offset += 6
        return out_appdata

# 设置路由工作模式
    def packAppdata_AFN11Fn04(self, working_condition: int, allow_status: int, nbackup: int, Error_Correction: int, comm_speed: int, units: int):
        self.iAFN = 0x11  # 输入的功能码
        self.iFn = 4  # 输入的Fn
        # working_condition : 工作状态 1：学习 0：抄表 1bit
        # allow_status: 注册允许状态 1：允许 0：不允许 1bit
        # nbackup：备用 2bit
        # Error_Correction: 纠错编码 4bit ()
        # comm_speed：通信速率 15bit
        # units：速率单位 1bit
        work_mode = AFN11Fn04_WORK_MODE()
        work_mode.working_condition = working_condition
        work_mode.allow_status = allow_status
        work_mode.nbackup = nbackup
        work_mode.Error_Correction = Error_Correction
        work_mode.comm_speed = comm_speed
        work_mode.units = units
        out_appdata = (u8*3)()
        memmove(addressof(out_appdata), addressof(work_mode), 3)
        return out_appdata

# 激活从节点主动注册
    def packAppdata_AFN11Fn05(self, start_time: str, duration_time: int, repeat_count: int, time_slice: int):
        self.iAFN = 0x11  # 输入的功能码
        self.iFn = 5  # 输入的Fn
        # start_time：起始时间 6bytes(BCD) 秒-分-时-日-月-年 输入时可以是 年-月-日-时-分-秒
        # duration_time: 持续时间 2byte 单位 min
        # repeat_count：从节点重发次数 1byte
        # time_slice：随机等待时间片 1byte 150ms一个片段
        start_time = start_time.replace('-', '')
        start_time_bytes = bytes.fromhex(start_time)
        out_appdata = (u8*10)()
        out_appdata[0:6] = start_time_bytes[5], start_time_bytes[4], start_time_bytes[
            3], start_time_bytes[2], start_time_bytes[1], start_time_bytes[0]
        m_duration_time = (u16*1)(duration_time)
        memmove(addressof(out_appdata)+6, addressof(m_duration_time), 2)
        out_appdata[8] = repeat_count
        out_appdata[9] = time_slice
        return out_appdata

# 终止从节点主动注册，无数据单元
    def packAppdata_AFN11Fn06(self):
        self.iAFN = 0x11  # 输入的功能码
        self.iFn = 6  # 输入的Fn
        out_appdata = (u8*0)()
        return out_appdata

# 路由重启,无数据单元
    def packAppdata_AFN12Fn01(self):
        self.iAFN = 0x12  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        out_appdata = (u8*0)()
        return out_appdata

# 路由暂停,无数据单元
    def packAppdata_AFN12Fn02(self):
        self.iAFN = 0x12  # 输入的功能码
        self.iFn = 2  # 输入的Fn
        out_appdata = (u8*0)()
        return out_appdata

# 路由恢复,无数据单元
    def packAppdata_AFN12Fn03(self):
        self.iAFN = 0x12  # 输入的功能码
        self.iFn = 3  # 输入的Fn
        out_appdata = (u8*0)()
        return out_appdata

# 监控从节点
    def packAppdata_AFN13Fn01(self, comm_protocol=None, Comm_delay_flag=None, Num_affiliated_nodes=None,  message_len=None, message=None):
        self.iAFN = 0x13  # 输入的功能码
        self.iFn = 1  # 输入的Fn
        # comm_protocol: 通信协议类型
        # Comm_delay_flag:通信延迟相关标志
        # Num_affiliated_nodes:附属节点数量
        # message_len: 报文长度
        # message:  报文内容
        addrs = sAddr()
        out_appdata = (u8 * (message_len + 4+(6*Num_affiliated_nodes)))()
        offset = 0
        out_appdata[0:3] = comm_protocol, Comm_delay_flag, Num_affiliated_nodes
        offset += 3
        if Num_affiliated_nodes > 0:
            for i in range(0, Num_affiliated_nodes, 1):
                memmove(addressof(out_appdata) + offset, addressof(addrs), 6)
                i += 1
                offset += 6
        else:
            pass
        out_appdata[offset] = message_len
        offset += 1
        memmove(addressof(out_appdata) + offset,
                addressof(message), message_len)
        offset += message_len
        return out_appdata

# 路由请求抄读内容
    def packAppdata_AFN14Fn01(self, read_mark: int, Comm_delay_flag: int, data_length: int, message: POINTER(u8), Num_affiliated_nodes: int, addrs_list: list):
        self.iAFN = 0x14  # 输入的功能码
        self.iFn = 1  # 输入的Fn

    def unpackAppdata_AFN06Fn05(self, input_data=None):
        return 1

    def byte_arr2hex(self, arr, sep: str, rlen=0):
        if (rlen == 0):
            return ''
        tmpLen = len(arr)
        if rlen > 0 and (tmpLen > rlen):
            tmpLen = rlen
        tmp = sep.join(['{:02X}'.format(arr[i]) for i in range(tmpLen)])
        # tmp = len(arr)
        return tmp

    def GetOffsetData(self, pData, offset, Len):
        data = (c_uint8 * Len).from_address(addressof(pData.contents) + offset)
        return data

#   将数据帧转换为可发送的串口字节码bytes型
    def sendbuff_2_bytes(self):
        if self.m_offset > 0:
            send_bytes = bytes.fromhex(self.byte_arr2hex(
                self.sendBuff, '', self.m_offset))
        else:
            send_bytes = None
        return send_bytes


if __name__ == '__main__':
    import re
    import binascii

    # tmpStr = '68 1C 00 41 0C 00 00 00 00 02 00 00 00 00 00 00 86 21 97 11 00 13 F0 04 19 00 BE 16'
    # tmpStr = re.sub(r' ', "", tmpStr)
    # print('tmpStr', tmpStr)
    # frame = bytes().fromhex(tmpStr)
    # # print('frame ', binascii.b2a_hex(frame).decode('utf-8').upper(), len(frame))
    # rxData = (u8 * len(frame)).from_buffer_copy(frame)
    # print(['{:02X}'.format(i) for i in rxData])
    # print(rxData, hex(rxData[0]), hex(rxData[-1]))
    jsonFileName = 'D:\Documents\VSCode\SmartTTU\dlms_plc\GDW1372\kwh_list_cco.json'
    jsonFile = open(jsonFileName, 'r')
    jsonFileLoad = json.loads(jsonFile.read())
    meterConf = []
    for v in jsonFileLoad:
        meterConf.append(v)

    listMeter1Phasa_asli = []
    listMeter3Phasa_asli = []
    listMeter1Phasa = []
    listMeter3Phasa = []
    makeList = []
    counter = 0
    for i in meterConf:
        for v in i['serialNumber']:
            if i['type'] == 1:
                listMeter1Phasa.append([v[::-1], counter])
                counter += 1
                makeList.append([v[::-1], counter])
            if i['type'] == 3:
                listMeter3Phasa.append([v[::-1], counter])
                counter += 1
                makeList.append([v[::-1], counter])
    print(makeList)
    # print(listMeter1Phasa)
    # print(listMeter3Phasa)

    gw = GW376_2Base()
    # gw.get376_2Info(rxData, sizeof(rxData))
    print('{:02x}'.format(gw.Recv376_2Info.AFN))
    gw.setCCO_MAC('010203040506')
    gw.setSTA_MAC('000000000035')
    # m_message = (u8 * 16)(0x68, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0x68, 0x14, 0x04, 0x33, 0x33, 0x33, 0x33,
    #   0x13, 0x16)
    # send1, mylen = gw.make376_2frame(
    #     sMAC=gw.CCO_MAC,           # Original address
    #     dMAC=gw.STA_MAC,           # target address
    #     bComModuleFlag=1,          # Communication module logo
    #     ucFrameSn=100,             # Frame sequence number
    #     user_data=gw.packAppdata_AFN11Fn05(start_time='21-04-25-15-04-00', duration_time=10, repeat_count=3, time_slice=20))

    send1, mylen = gw.make376_2frame(
        sMAC=gw.CCO_MAC,           # Original address
        dMAC=gw.STA_MAC,           # target address
        bComModuleFlag=1,          # Communication module logo
        ucFrameSn=100,             # Frame sequence number
        user_data=gw.packAppdata_AFN11Fn01(number=len(makeList), addrs_list=makeList))
    print(gw.byte_arr2hex(send1, '', mylen))
    print(gw.sendbuff_2_bytes())
    pass
