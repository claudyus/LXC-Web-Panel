class LxcConfigFileNotComplete(Exception):
    pass


class ContainerNotExists(Exception):
    pass


class ContainerAlreadyExists(Exception):
    pass


class ContainerDoesntExists(Exception):
    pass


class ContainerAlreadyRunning(Exception):
    pass


class ContainerNotRunning(Exception):
    pass


class DirectoryDoesntExists(Exception):
    pass


class NFSDirectoryNotMounted(Exception):
    pass
