from setuptools import Extension, setup
from setuptools.command.build_py import build_py


class CustomInstallCommand(build_py):
    def run(self):
        print("Compiling ws2805 library...")
        super().run()


setup(
    cmdclass={"build_py": CustomInstallCommand},
    ext_modules=[
        Extension(
            "_rpi_ws2805",
            include_dirs=["."],
            sources=[
                "rpi_ws2805_wrap.c",
                "lib/dma.c",
                "lib/mailbox.c",
                "lib/main.c",
                "lib/pcm.c",
                "lib/pwm.c",
                "lib/rpihw.c",
                "lib/ws2805.c",
            ],
        )
    ],
)
