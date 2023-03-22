class Device(object):
    '''Define device abstract class'''
    def __init__(self, device, rst_port, phi_port, phi_bar_port, update_port,
                 capture_port, scan_in_port, scan_out_port):
        self.rst = device(rst_port, "O")
        self.phi = device(phi_port, "O")
        self.phi_bar = device(phi_bar_port, "O")
        self.scan_in = device(scan_in_port, "O")
        self.update = device(update_port, "O")
        self.capture = device(capture_port, "O")
        self.scan_out = device(scan_out_port, "I")
