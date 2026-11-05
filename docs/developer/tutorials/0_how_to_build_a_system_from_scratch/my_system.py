import cpu.iss.riscv
import gdbserver.gdbserver
import gvsoc.runner
import gvsoc.systree
import interco.router
import memory.memory
import utils.loader.loader
import vp.clock_domain

GAPY_TARGET = True

class Target(gvsoc.runner.Target):

    def __init__(self, parser, options):
        super().__init__(parser, options,
               model=Rv64, description="RV64 virtual board")


class Rv64(gvsoc.systree.Component):

    def __init__(self, parent, name, parser, options):
        super().__init__(parent, name, options=options)

        clock = vp.clock_domain.Clock_domain(self, 'clock', 100_000_000) # 100MH

        soc = Soc(self, 'soc', parser)
        clock.o_CLOCK(soc.i_CLOCK())


class Soc(gvsoc.systree.Component):

    def __init__(self, parent, name, parser):
        super().__init__(parent, name)

        # Parse the arguments to get the path to the binary to be loaded
        [args, __] = parser.parse_known_args()

        binary = args.binary

        mem_size = 0x00_10_00_00
        mem = memory.memory.Memory(self, 'mem', size=mem_size) # 1MB

        ico = interco.router.Router(self, 'ico')
        ico.o_MAP(mem.i_INPUT(), mem.name, base=0x00_00_00_00, remove_offset=0x00_00_00_00, size=mem_size)

        host = cpu.iss.riscv.Riscv(self, 'host', isa='rv64imafdc')
        host.o_FETCH(ico.i_INPUT())
        host.o_DATA(ico.i_INPUT())
        host.o_DATA_DEBUG(ico.i_INPUT())

        loader = utils.loader.loader.ElfLoader(self, 'loader', binary=binary)
        loader.o_OUT     (ico.i_INPUT    ())
        loader.o_START   (host.i_FETCHEN ())
        loader.o_ENTRY   (host.i_ENTRY   ())

        gdbserver.gdbserver.Gdbserver(self, 'gdbserver')