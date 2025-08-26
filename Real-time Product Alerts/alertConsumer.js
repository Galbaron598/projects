const { Kafka } = require("kafkajs")
const Redis = require("ioredis")

// Kafka and Redis config
const KAFKA_BROKER = "localhost:9092"
const REDIS_HOST = "localhost"

const kafka = new Kafka({
  clientId: "alert-consumer",
  brokers: [KAFKA_BROKER],
})

const consumer = kafka.consumer({ groupId: "alert-group" })
const redis = new Redis({ host: REDIS_HOST, port: 6379 })

// Main function
const run = async () => {
  await consumer.connect()
  await consumer.subscribe({ topic: "alerts", fromBeginning: true })

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      const alert = JSON.parse(message.value.toString())

      // Save alert JSON in Redis list
      await redis.lpush("alerts", JSON.stringify(alert))
      await redis.ltrim("alerts", 0, 99); // keep only last 100 alerts

      console.log("🚨 Alert stored in Redis:", alert)
    },
  });
};

// Start consumer
run().catch(console.error)
