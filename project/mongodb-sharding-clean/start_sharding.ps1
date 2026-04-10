# =========================
# CLEAN SHARDING START SCRIPT
# =========================

# =========================
# CLEAN SHARDING START SCRIPT
# =========================

Write-Host "Stopping existing MongoDB processes..."
taskkill /f /im mongod.exe 2>$null
taskkill /f /im mongos.exe 2>$null


Start-Sleep -Seconds 2

Write-Host "Starting Config Server..."
Start-Process mongod -ArgumentList "--configsvr --replSet cfgrs2 --port 27119 --dbpath ./config" -NoNewWindow
Start-Sleep -Seconds 3

mongosh --port 27119 --eval '
rs.initiate({
  _id: "cfgrs2",
  configsvr: true,
  members: [{ _id: 0, host: "localhost:27119" }]
})
'

Write-Host "Starting Shard A..."
Start-Process mongod -ArgumentList "--shardsvr --replSet shardA --port 27121 --dbpath ./shard1" -NoNewWindow
Start-Sleep -Seconds 3

mongosh --port 27121 --eval '
rs.initiate({
  _id: "shardA",
  members: [{ _id: 0, host: "localhost:27121" }]
})
'

Write-Host "Starting Shard B..."
Start-Process mongod -ArgumentList "--shardsvr --replSet shardB --port 27122 --dbpath ./shard2" -NoNewWindow
Start-Sleep -Seconds 3

mongosh --port 27122 --eval '
rs.initiate({
  _id: "shardB",
  members: [{ _id: 0, host: "localhost:27122" }]
})
'

Write-Host "Starting Mongos..."
Start-Process mongos -ArgumentList "--configdb cfgrs2/localhost:27119 --port 27120" -NoNewWindow
Start-Sleep -Seconds 5

Write-Host "Adding Shards and Enabling Sharding..."
mongosh --port 27120 --eval '
sh.addShard("shardA/localhost:27121")
sh.addShard("shardB/localhost:27122")

sh.enableSharding("forkliftDB_clean")

use forkliftDB_clean

db.createCollection("telemetry_by_forklift")
db.telemetry_by_forklift.createIndex({ forklift_id: "hashed" })

sh.shardCollection(
  "forkliftDB_clean.telemetry_by_forklift",
  { forklift_id: "hashed" }
)

db.createCollection("telemetry_by_time")
db.telemetry_by_time.createIndex({ timestamp: 1 })

sh.shardCollection(
  "forkliftDB_clean.telemetry_by_time",
  { timestamp: 1 }
)
'

Write-Host "Sharding cluster started successfully!"