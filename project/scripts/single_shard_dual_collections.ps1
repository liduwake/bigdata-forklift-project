# ================================
# MongoDB Single Shard Setup Script
# ================================

Write-Host "Checking admin privileges..."

if (-NOT ([Security.Principal.WindowsPrincipal] 
    [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltinRole]::Administrator)) {

    Write-Host "❌ Please run PowerShell as Administrator"
    exit
}

Write-Host "✅ Running as Administrator"

# -------------------------------
# Check Ports
# -------------------------------
$ports = @(27017, 27018, 27019)

foreach ($port in $ports) {
    $result = netstat -ano | findstr $port
    if ($result) {
        Write-Host "❌ Port $port is already in use"
        exit
    } else {
        Write-Host "✅ Port $port is free"
    }
}

# -------------------------------
# Start Config Server
# -------------------------------
Start-Process mongod -ArgumentList "--configsvr --replSet cfgrs --port 27019 --dbpath ./config" -NoNewWindow

Start-Sleep -Seconds 3

mongosh --port 27019 --eval '
rs.initiate({
  _id: "cfgrs",
  configsvr: true,
  members: [{ _id: 0, host: "localhost:27019" }]
})
'

# -------------------------------
# Start Shard (single)
# -------------------------------
Start-Process mongod -ArgumentList "--shardsvr --replSet shard1 --port 27018 --dbpath ./shard1" -NoNewWindow

Start-Sleep -Seconds 3

mongosh --port 27018 --eval '
rs.initiate({
  _id: "shard1",
  members: [{ _id: 0, host: "localhost:27018" }]
})
'

# -------------------------------
# Start Mongos
# -------------------------------
Start-Process mongos -ArgumentList "--configdb cfgrs/localhost:27019 --port 27017" -NoNewWindow

Start-Sleep -Seconds 3

# -------------------------------
# Add Shard + Enable Sharding
# -------------------------------
mongosh --port 27017 --eval '
sh.addShard("shard1/localhost:27018")

sh.enableSharding("forkliftDB")

use forkliftDB

db.createCollection("telemetry_by_forklift")
db.telemetry_by_forklift.createIndex({ forklift_id: "hashed" })

sh.shardCollection(
  "forkliftDB.telemetry_by_forklift",
  { forklift_id: "hashed" }
)

db.createCollection("telemetry_by_time")
db.telemetry_by_time.createIndex({ timestamp: 1 })

sh.shardCollection(
  "forkliftDB.telemetry_by_time",
  { timestamp: 1 }
)
'

Write-Host "🎉 Single shard + dual collections setup complete"