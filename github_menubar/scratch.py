def server_running(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", port))
        result = False
    except OSError:
        result = True
    sock.close()
    return result

        if not server_running(CONFIG["port"]):
            server_thread = threading.Thread(target=run_server)
            server_thread.start()
        # response = requests.get(f"http://127.0.0.1:{CONFIG['port']}/state")
        # return json.loads(response.content)
        while True:
            try:
                response = requests.get(f"http://127.0.0.1:{CONFIG['port']}/state")
                return json.loads(response.content)
            except requests.ConnectionError:
                time.sleep(1)

    @property
    def _server_pid(self):
        return subprocess.getoutput(f"lsof -i:{CONFIG['port']} -t")

                # self._section_break()
        # print(f"kill server | font={CONFIG['font']} bash=kill param1={self._server_pid} terminal=true")
