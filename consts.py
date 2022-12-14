import datetime


class Const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("can't change const %s" % name)
        if not name.isupper():
            raise self.ConstCaseError('const name "%s" is not all uppercase' % name)
        self.__dict__[name] = value


const = Const()
const.LOCAL_ZIP_DIR = "D:/cars/zip"
const.LOCAL_PDF_DIR = "D:/cars/pdf"
day = datetime.datetime.now().strftime('%Y-%m-%d')
const.CSV_FILE_DIR = "d:/cars/csv"
const.CSV_FILE_PATH = "d:/cars/csv/" + "car_maintenance_" + day + ".csv"
