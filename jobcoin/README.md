This coding exercise makes some assumptions

1. We don't have a P2P network
2. We are assuming the client will send withdrawal addresses in the command line
3. Sender will also specify percentage of amounts to be sent to the withdrawal addresses Ex: [10,90] implies 10% to account 1 and 90% to account 2
4. We are also assuming the identity of the sender. This would have to be verified in a production setup

5. The deposit address is specified by the end user. We possibly want to have separate deposit addresses for the users.  This mapping has to be persisted in the Database

6. For the amounts that will be transferred from the home address to the withdrawal addresses, we have divided them based on percentages.

7. For the transfers from the users' address to the deposit address, we may want to consider a task queue for it and post the transactions/transfers there.  This task queue will have multiple workers to initiate the transfers and wait until completion or timeout.

8. In order to implement a queuing system, we need a way to see all the pending transfers. For this we need a job tracking system and for each task/job that is being processed, the job id is generated.  Hadoop with zookeeper would work well here with Yarn as a job scheduler.  We could also consider Celery with zookeeper/RabbitMQ as the broker and Redis to hold the results of the jobs.

9. For the watcher we could use an event based architecture where the transfer from user to the deposit address triggers an event and then the event is pushed to a queue to be processed. We could use Kafka for the queue and then the consumer would the service that transfers the bitcoin from the deposit address to the home address. For the transfer from the deposit to home address and subsequently to the withdrawal accounts, we must use a scheduler to transfer. Yarn as job scheduler with hadoop will work here well. Or we could use celery here.

10. One more important aspect of this system is that all the transfers will not be instantaneous.  There will be a delay in completing the transfer. So we should maintain the status of each transfer additionally to know when it's initiated, completed or failed.  

9. We should also have a Dead Letter Queue for failed jobs.  We should be able to retry the transfer for n number of times that we have configured based on the failures. Some failures should not be retried. For ex: 500 error. We have to carefully design the system to make sure what HTTP status should be considered for retries 