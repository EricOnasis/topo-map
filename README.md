# topo-map

Pull network topology from RouterOS's own neighbor discovery (`/ip neighbor print`, MikroTik's
equivalent of CDP/LLDP) — no manual documentation to keep in sync with reality.

## Installation

```sh
pip install -r requirements.txt
```

## Usage

```sh
cp inventory.example.json inventory.json   # fill in your devices
python topomap.py inventory.json
```

```
core-router --[ether1]--> branch-switch (192.168.88.5)
```

Or as JSON:

```sh
python topomap.py inventory.json --json
```

Diagram rendering (Mermaid) coming soon.

## License

MIT — see [LICENSE](LICENSE).
