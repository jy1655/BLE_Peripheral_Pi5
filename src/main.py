from gi.repository import GLib
import sys
from dbus import SystemBus
from dbus.mainloop.glib import DBusGMainLoop
from ble_manager import BLEManager
import ble_auto_confirm
import argparse




def main(timeout=0):
    
    # Set up the main event loop for D-Bus and GLib.
    DBusGMainLoop(set_as_default=True)
    bus = SystemBus()
    mainloop = GLib.MainLoop()

    # Register an agent to automatically handle BLE pairing requests.
    ble_auto_confirm.register_agent(bus)

    # Initialize the BLE Manager
    ble_manager = BLEManager(bus, mainloop)

    # Set up and register the GATT services your device offers.
    print("Starting Gatt")
    ble_manager.registering_gatt()

    # Kick off BLE advertising to make your device discoverable.
    print("Starting BLE Advertising...")
    ble_manager.start_advertising()


    if timeout > 0:
        # If a timeout is specified, run the advertising for a limited time.
        # threading.Thread(target=BLEManager.shutdown(timeout), args=(timeout,)).start
        GLib.timeout_add_seconds(timeout, mainloop.quit)
    else:
        # Otherwise, keep advertising until manually stopped.
        print('Advertising forever...')

    try:
        # Start the GLib main loop
        mainloop.run()
    except KeyboardInterrupt:
        print("EXITING NOW...")
    #    ble_manager.disconnect_all_devices()

    finally:
        # Provide a graceful shutdown mechanism.
        ble_manager.stop_advertising()
        sys.exit(0)


if __name__ == "__main__":
    # Parse command line arguments for optional advertising timeout
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', default=0, type=int, help="advertise " +
                        "for this many seconds then stop, 0=run forever " +
                        "(default: 0)")
    args = parser.parse_args()
    
    # Run the main function with the specified timeout.
    main(args.timeout)