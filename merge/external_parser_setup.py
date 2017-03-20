
class ExternalParserSetup:
    is_set = False

    @classmethod
    def setup(cls):
        if not cls.is_set:
            cls.is_set = True
            from clang.cindex import Config
            Config.set_library_file("/usr/local/opt/llvm/lib/libclang.dylib")