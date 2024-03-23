import os
import sys
import traceback
from gurux_serial import GXSerial
from gurux_net import GXNet
from gurux_dlms.enums import ObjectType
from gurux_dlms.objects.GXDLMSObjectCollection import GXDLMSObjectCollection
from GXDLMSReader import GXDLMSReader
from gurux_dlms.GXDLMSClient import GXDLMSClient
from gurux_common.GXCommon import GXCommon
from gurux_dlms.enums.DataType import DataType
from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader
import locale
from gurux_dlms.GXDateTime import GXDateTime
from gurux_dlms.internal._GXCommon import _GXCommon
from gurux_dlms import GXDLMSException, GXDLMSExceptionResponse, GXDLMSConfirmedServiceError, GXDLMSTranslator
from gurux_dlms import GXByteBuffer, GXDLMSTranslatorMessage, GXReplyData
from gurux_dlms.enums import RequestTypes, Security, InterfaceType
from gurux_dlms.secure.GXDLMSSecureClient import GXDLMSSecureClient
from gurux_dlms.objects import GXDLMSObject, GXDLMSObjectCollection, GXDLMSData, GXDLMSRegister,\
    GXDLMSDemandRegister, GXDLMSProfileGeneric, GXDLMSExtendedRegister
import json
import re
import os


try:
    import pkg_resources
    # pylint: disable=broad-except
except Exception:
    # It's OK if this fails.
    print("pkg_resources not found")


class sampleclient():
    @classmethod
    def main(cls, args):
        # try:
        #     print("gurux_dlms version: " +
        #           pkg_resources.get_distribution("gurux_dlms").version)
        #     print("gurux_net version: " +
        #           pkg_resources.get_distribution("gurux_net").version)
        #     print("gurux_serial version: " +
        #           pkg_resources.get_distribution("gurux_serial").version)
        # except Exception:
        #     # It's OK if this fails.
        #     print("pkg_resources not found")

        # args: the command line arguments
        reader = None
        settings = GXSettings()
        try:
            # //////////////////////////////////////
            #  Handle command line parameters.
            ret = settings.getParameters(args)
            if ret != 0:
                return
            # //////////////////////////////////////
            #  Initialize connection settings.
            if not isinstance(settings.media, (GXSerial, GXNet)):
                raise Exception("Unknown media type.")
            # //////////////////////////////////////
            reader = GXDLMSReader(
                settings.client, settings.media, settings.trace, settings.invocationCounter)
            settings.media.open()
            if settings.readObjects:
                read = False
                reader.initializeConnection()
                # if settings.outputFile and os.path.exists(settings.outputFile):
                #     try:
                #         c = GXDLMSObjectCollection.load(settings.outputFile)
                #         settings.client.objects.extend(c)
                #         if settings.client.objects:
                #             read = True
                #     except Exception:
                #         read = False
                # if not read:
                # reader.getAssociationView()

                obis = "0.0.96.1.0.255"
                obj2 = GXDLMSData(obis)
                sn = reader.read(obj2, 2)
                # print(sn)

                obis = "1.0.32.7.0.255"
                obj2 = GXDLMSRegister(obis)
                volt = reader.read(obj2, 3)
                volt = reader.read(obj2, 2)
                # print(volt)

                obis = "1.0.31.7.0.255"
                obj2 = GXDLMSRegister(obis)
                curr = reader.read(obj2, 3)
                curr1 = reader.read(obj2, 2)
                # print(curr1)

                obis = "1.0.21.7.0.255"
                obj2 = GXDLMSRegister(obis)
                watt = reader.read(obj2, 3)
                watt1 = reader.read(obj2, 2)
                # print(watt1)

                obis = "1.0.33.7.0.255"
                obj2 = GXDLMSRegister(obis)
                pf = reader.read(obj2, 3)
                pf1 = reader.read(obj2, 2)
                # print(pf1)

                obis = "1.0.14.7.0.255"
                obj2 = GXDLMSRegister(obis)
                freq = reader.read(obj2, 3)
                freq1 = reader.read(obj2, 2)
                # print(freq1)

                obis = "1.0.1.8.0.255"
                obj2 = GXDLMSRegister(obis)
                kwh = reader.read(obj2, 3)
                kwh1 = reader.read(obj2, 2)
                # print(kwh1)

                obis = "1.0.2.8.0.255"
                obj2 = GXDLMSRegister(obis)
                kwh = reader.read(obj2, 3)
                kwh2 = reader.read(obj2, 2)
                # print(kwh2)

                obis = "1.0.3.8.0.255"
                obj2 = GXDLMSRegister(obis)
                kvar = reader.read(obj2, 3)
                kvar1 = reader.read(obj2, 2)
                # print(kvar1)

                obis = "1.0.4.8.0.255"
                obj2 = GXDLMSRegister(obis)
                kvar = reader.read(obj2, 3)
                kvar2 = reader.read(obj2, 2)
                # print(kvar2)

                lists = [
                    {
                        "name": "sn",
                        "val": sn,
                        "unit": "null"
                    },
                    {
                        "name": "Volt",
                        "val": str(volt),
                        "unit": "V"
                    },
                    {
                        "name": "Current",
                        "val": str(curr1),
                        "unit": "A"
                    },
                    {
                        "name": "Watt",
                        "val": str(watt1),
                        "unit": "W"
                    },
                    {
                        "name": "pF",
                        "val": str(pf1),
                        "unit": "null"
                    },
                    {
                        "name": "Freq",
                        "val": str(freq1),
                        "unit": "Hz"
                    },
                    {
                        "name": "KWH",
                        "val": str(kwh1),
                        "unit": "V"
                    }
                ]
                strr = "{"+str(lists)+"}"
                # print(strr)
                dump_json = json.dumps(lists)
                print(dump_json)
                dt_escape = dump_json.replace('"', re.escape('\"'))
                os.system(
                    "mosquitto_pub -h 203.194.112.238 -m {0} -u das -P mgi2022 -t test/DLMS".format(dt_escape))
                # print(dt_escape)

                # for k, v in settings.readObjects:
                #     print(k, v)
                #     obj = settings.client.objects.findByLN(ObjectType.NONE, k)
                #     # if obj is None:
                #     #     raise Exception("Unknown logical name:" + k)
                #     val = reader.read(obj, v)
                #     reader.showValue(v, val)
                # if settings.outputFile:
                #     settings.client.objects.save(settings.outputFile)
            else:
                reader.readAll(settings.outputFile)
        except (ValueError, GXDLMSException, GXDLMSExceptionResponse, GXDLMSConfirmedServiceError) as ex:
            print(ex)
        except (KeyboardInterrupt, SystemExit, Exception) as ex:
            traceback.print_exc()
            if settings.media:
                settings.media.close()
            reader = None
        finally:
            if reader:
                try:
                    reader.close()
                except Exception:
                    traceback.print_exc()
            print("Ended. Press any key to continue.")


if __name__ == '__main__':

    sampleclient.main(sys.argv)
