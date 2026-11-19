import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "wifi_engineer.py"
spec = importlib.util.spec_from_file_location("wifi_engineer", SOURCE)
wifi = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(wifi)

class IPTests(unittest.TestCase):
    def test_ipv4_24(self):
        r=wifi.calculate_network("192.168.10.14/24")
        self.assertEqual(r["network"],"192.168.10.0")
        self.assertEqual(r["broadcast"],"192.168.10.255")
        self.assertEqual(r["first_usable"],"192.168.10.1")
        self.assertEqual(r["last_usable"],"192.168.10.254")
        self.assertEqual(r["num_addresses"],256)
    def test_ipv6(self):
        r=wifi.calculate_network("2001:db8::10/64")
        self.assertEqual(r["version"],6)
        self.assertEqual(r["network"],"2001:db8::")
        self.assertIsNone(r["broadcast"])
    def test_invalid_address(self):
        with self.assertRaises(wifi.DiagnosticError): wifi.calculate_network("192.168.1.999/24")
    def test_ipv4_31(self):
        r=wifi.calculate_network("192.0.2.1/31")
        self.assertEqual(r["first_usable"],"192.0.2.0")
        self.assertEqual(r["last_usable"],"192.0.2.1")

class ValidationTests(unittest.TestCase):
    def test_port_bounds(self):
        with self.assertRaises(wifi.DiagnosticError): wifi.tcp_check("127.0.0.1",0)
    def test_ping_count_bounds(self):
        with self.assertRaises(wifi.DiagnosticError): wifi.ping_host("127.0.0.1",21)
    def test_trace_hops_bounds(self):
        with self.assertRaises(wifi.DiagnosticError): wifi.trace_route("localhost",100)
    def test_dns_type(self):
        with self.assertRaises(wifi.DiagnosticError): wifi.resolve_dns("localhost","MX")

class ReportTests(unittest.TestCase):
    def test_json_report(self):
        with tempfile.TemporaryDirectory() as d:
            p=wifi.write_report({"healthy":True},str(Path(d)/"sub"/"r.json"),"json")
            self.assertTrue(p.exists())
            self.assertIn('"healthy": true',p.read_text(encoding="utf-8"))

if __name__=="__main__": unittest.main()
