# Ethereum Hive Simulators Python Library

Write hive simulators using python

## Run tests

#### Fetch and build hive:

```bash
git clone https://github.com/ethereum/hive.git
cd hive
go build -v .
```

#### Run hive in dev mode
```bash
./hive --dev --client go-ethereum,lighthouse-bn,lighthouse-vc
```

#### Run tests
```bash
pytest
```