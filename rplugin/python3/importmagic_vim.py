import threading

import importmagic
import pynvim

g_nvim = None
g_index = None
g_index_built = False
g_index_path = None


def as_thread(target, *a, **b):
    def _target():
        try:
            t.result = target()
        except Exception as exc:
            t.failure = exc

    t = threading.Thread(target=_target, *a, **b)
    return t


@pynvim.plugin
class ImportMagicVim:
    def __init__(self, nvim):
        global g_nvim
        global g_index
        global g_index_built
        g_nvim = nvim
        g_index = importmagic.SymbolIndex()

    def _createindex(self):
        global g_index_built
        g_nvim.async_call(g_nvim.out_write, "Building importmagic index...\n")
        g_index.build_index(g_index_path)
        g_index_built = True
        g_nvim.async_call(g_nvim.out_write, "Importmagic index built\n")

    @pynvim.function("CreateIndex")
    def createIndex(self, _):
        global g_index_path
        a = g_nvim.command_output(
            "echo system('python -c \"import sys; print(sys.path)\"')"
        )
        g_index_path = eval(a)
        thread = as_thread(self._createindex)
        thread.start()
        # thread.join()
        # g_nvim.out_write(str(getattr(thread, "failure", None)) + "\n")
        # if getattr(thread, "failure", None):
        #     g_nvim.out_write("Failed: {}...\n".format(thread.failure))
        #     raise Exception(thread.failure)

    def updateSource(self, update=None):
        if not update:
            self.source = "\n".join(g_nvim.current.buffer[:])
        else:
            start, end, u = update
            tmp = self.source.splitlines()
            tmp[start:end] = u
            self.source = "\n".join(tmp)

    def get_update(self):
        self.updateSource()
        scope = importmagic.Scope.from_source(self.source)
        # self.nvim.out_write(repr(scope) + '\n')
        unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
        if unresolved or unreferenced:
            start_line, end_line, import_block = importmagic.get_update(
                self.source, g_index, unresolved, unreferenced
            )
            import_block = import_block.splitlines()[:-1]
            return start_line, end_line, import_block
        else:
            return None

    @pynvim.command("UpdateImports", nargs=0)
    def updateImports(self):
        if not g_index_built:
            g_nvim.err_write("Index is not built yet\n")
        else:
            update = self.get_update()
            if update:
                start_line, end_line, import_block = update
                g_nvim.current.buffer[start_line:end_line] = import_block
