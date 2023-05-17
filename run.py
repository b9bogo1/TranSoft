from waitress import serve
import TranSoft
from TranSoft.configs_local import get_node

NODE = get_node()

if __name__ == "__main__":
    serve(TranSoft.create_app(), host=NODE['ip'], port=NODE['port'])

