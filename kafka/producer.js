require('dotenv').config();
const { Kafka } = require('kafkajs');
const axios = require('axios');
const md5 = require('md5');

const kafka = new Kafka({
  clientId: 'news-producer',
  brokers: ['localhost:9092'],
});

const producer = kafka.producer();
const seenIds = new Set();

const run = async () => {
  await producer.connect();
  console.log('Connected to Kafka broker');

  // Fetch and send news articles every 30 seconds
  setInterval(async () => {
    try {
      const response = await axios.get('https://newsapi.org/v2/top-headlines', {
        params: {
          country: 'us',
          pageSize: 20,
          apiKey: process.env.NEWS_API_KEY,
        },
      });

      const articles = response.data.articles || [];

      for (const article of articles) {
        // Generate md5 hash of URL as ID
        const id = md5(article.url);

        // Skip if we've already sent this article
        if (seenIds.has(id)) {
          continue;
        }

        // Mark as seen
        seenIds.add(id);

        // Build payload
        const payload = {
          id,
          title: article.title || '',
          description: article.description || '',
          source: article.source?.name || 'Unknown',
          url: article.url || '',
          publishedAt: article.publishedAt || '',
        };

        // Send to Kafka topic
        await producer.send({
          topic: 'news_topic',
          messages: [
            {
              value: JSON.stringify(payload),
            },
          ],
        });

        console.log(`Sent: ${payload.title}`);
      }
    } catch (error) {
      console.error('Error fetching or sending news:', error.message);
    }
  }, 30000); // 30 seconds
};

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('Shutting down...');
  await producer.disconnect();
  process.exit(0);
});

run().catch(console.error);
