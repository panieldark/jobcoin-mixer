# Jobcoin Mixer - Daniel Park

<a href="http://cryptomixer.fun" target="_blank">http://cryptomixer.fun/</a>

<a href="https://www.figma.com/file/stYqqiSCeNj7b5a90lwXEJ/Jobcoin-Gemini-Daniel-Park?node-id=0%3A1" target="_blank">The Design (Figma)</a>
## Use Case

1. Navigate to <a href="http://cryptomixer.fun/mix/" target="_blank">http://cryptomixer.fun/mix/</a> and enter a starting address and up to five destination addresses
2. Copy the address given back, and deposit coins to this address (via the Jobcoin interface provided, <a href="https://jobcoin.gemini.com/kept-velvet" target="_blank">here</a>)
3. Sit back and wait for your coins to be deposited to the addresses you provided.

Some things to note:

- The amount deposited will be split amongst the destination addresses evenly
- There is a 3% mixing service fee incurred with every deposit

## Mixer process (at a lower level)

- When the user submits the destination addresses form, a MixerRequest is created with the following information stored:

  ![mixer request stub](https://jobcoin-mixer.s3.amazonaws.com/static/media/mixerrequest.png)

- An AWS Lambda function is set to scan the network (via calls to the Jobcoin transactions API endpoint) for any payments matching information stored across any open requests (currently set to scan every 10 minutes)

  - to reduce the number of transactions needed to be scanned, the lambda function utilizes a simple caching mechanism, allowing it to review only new transactions

- Upon sight of a new transaction, the lambda function pings a particular CryptoMixer web server endpoint, beginning the mixing process.

- The mixing process utilizes a set of reserve wallets (which, in practice, would be rotated/refreshed programmatically) within which the coins are mixed (after taking a 3% fee, amongst a set of wallets held by CryptoMixer).
  For each destination address, a path of wallets is randomly selected:
  - This path varies in the percentage of total amount sent (currently between 9-23%), the number of wallets in the path (currently 2-5 wallets), and the path of the wallets themselves (randomly selected amongst the pool of reserve wallets), before ending at the resulting addresses

### The tech (simplified):

![tech, simplified](https://jobcoin-mixer.s3.amazonaws.com/static/media/tech.png)

### Improvements/Nice-To-Haves with an extended project timeline

- Make the destinations form dynamic (can scale up or down from UI)
- improvements to algorithm (if actually implemented for prod):
  - implement time-based sleep mechanism for payments, to scatter randomly across time (perhaps varied across several hours/days)
  - vary the amount sent across per iteration of reserve wallets
  - maintain proper scale of the reserve wallets utilized (peg the number of house wallets to the size of the network)
  - scale the mixing process horizontally, by breaking the mixing pipeline in stages as to utilize multiple servers
  - tweak the randomness parameters as necessary to balance privacy and runtime (definitely room to utilize more runtime in this case)
- Better healthchecks/fail gracefully mechanisms
- Email notifications via mailchimp/Amazon SQS/other TPA, both for the mixing service (for customers on the ETA/status of their mixing requests) and for visibility into the pipeline/lambda services. ~~AWS should not be trusted~~ Anything can happen to services over a continued span of time
