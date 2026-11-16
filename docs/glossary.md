# Glossary

Terms used across this site, as they apply to private messaging. A tooltip shows the first paragraph of the matching entry; "Read more" opens the rest of it.

## Address portability

The ability to change the provider that serves you without changing the address other people use to reach you, as with a mobile phone number. In telephony the operators do it; on the web it usually depends on a domain that can be re-pointed to another host.

A POPOPX contact link names a message queue on the SMP server its owner chose, so the address of a connection describes that queue rather than a domain that could silently resolve elsewhere.

## Anonymous credentials

A value that authorizes an action without identifying who performs it: access to a resource is proved by presenting the credential, not by naming a person.

POPOPX apps hold one random credential per message queue, so an SMP server can accept or reject operations on a queue while knowing nothing about which user or which contact that queue belongs to.

## Blockchain

An ordered sequence of records in which every record carries a cryptographic hash of the record before it, so changing or removing any earlier record changes every identity that follows. The word is often used as a synonym for a distributed ledger, which adds a peer community and a consensus rule on top of the hash chain.

SMP queues use the narrower construction: messages are numbered in sequence and each includes the hash of the previous message, which lets the recipient detect a message that was inserted, removed or reordered. A blockchain is the linear special case of a [Merkle directed acyclic graph](https://popopx.chat/docs/glossary.md#merkle-directed-acyclic-graph).

## Break-in recovery

See [Post-compromise security](https://popopx.chat/docs/glossary.md#post-compromise-security).

## Centralized network

A network whose servers, address space and service state are operated by one entity. Signal, WhatsApp and Telegram are usually described this way.

A single operator can change the service quickly and is one place to fix a security problem, but it is also a single point of failure and a single place where connection metadata can be stored, subpoenaed or leaked.

## Content padding

See [Message padding](https://popopx.chat/docs/glossary.md#message-padding).

## Decentralized network

A network with no central authority and no state that every participant has to agree on: anyone can run a server, and the specification rather than an operator is the only shared dependency. Such networks resist censorship and outlive any single provider, at the cost of slower change.

POPOPX fits this only in part: its SMP relays are independent, they never exchange messages with one another and hold no user directory, so a user can run a server of their own, while the clients themselves are built and released by one team.

## Defense in depth

Layering independent protections so that the failure of one does not expose the system. In messaging it means not resting on transport security, or on end-to-end encryption alone.

POPOPX combines a [double ratchet algorithm](https://popopx.chat/docs/glossary.md#double-ratchet-algorithm) with a separate encryption layer per queue, TLS with strong cipher suites plus server fingerprint and channel binding checks, [message padding](https://popopx.chat/docs/glossary.md#message-padding) at each layer, and an optional [onion routing](https://popopx.chat/docs/glossary.md#onion-routing) transport.

## Double ratchet algorithm

The key agreement scheme that derives fresh encryption keys for every message by advancing two hash chains and adding a Diffie-Hellman step whenever a peer introduces a new key. Because the keys keep moving with the conversation, material recovered at one moment does not decrypt messages from another.

It gives both [forward secrecy](https://popopx.chat/docs/glossary.md#forward-secrecy) for messages sent before a compromise and [post-compromise security](https://popopx.chat/docs/glossary.md#post-compromise-security) for messages sent after it. POPOPX uses a double ratchet whose key exchange is post-quantum hybrid on every ratchet step, on by default in direct conversations.

## End-to-end encryption

Encryption in which only the devices at the two ends hold the keys, so the servers, relays and networks in between handle ciphertext at best. It protects message content, not metadata: who connects to which server, when and how often stays visible unless the network is designed to hide it.

In POPOPX messages are encrypted end to end with a [double ratchet algorithm](https://popopx.chat/docs/glossary.md#double-ratchet-algorithm), and each queue carries a further encryption layer, so an SMP server cannot read message content.

## Federated network

A network of separate servers run by different administrators that speak a common protocol and deliver to one another, as email, XMPP, Matrix and Mastodon do. Each instance sets its own rules, and interoperability requires a shared address space and mutual trust between servers.

POPOPX is not federated: relays never pass messages to other relays, and a message reaches its recipient only through the queues that recipient chose to receive on.

## Forward secrecy

The property that keys taken from a compromised device cannot decrypt traffic that was recorded earlier, because those session keys no longer exist anywhere and cannot be derived from the long-term secrets. "Perfect forward secrecy" names the same property; "perfect" is historical emphasis, not a stronger guarantee.

POPOPX gets it from the ephemeral Diffie-Hellman steps of the [double ratchet algorithm](https://popopx.chat/docs/glossary.md#double-ratchet-algorithm): messages sent before a compromise remain closed.

## Key agreement protocol

The procedure by which two parties establish a shared secret over a channel that they do not need to secure beforehand, so the secret can be used afterwards as an encryption key. Current protocols use Diffie-Hellman on elliptic curves, increasingly combined with a post-quantum key encapsulation.

The arithmetic is not the difficult part: the parties must also be sure that nobody substituted their own keys, which is the [man-in-the-middle attack](https://popopx.chat/docs/glossary.md#man-in-the-middle-attack) that verifying keys out of band addresses. POPOPX apps pass the one-time keys out of band, in an invitation link or a QR code.

## Key exchange

See [Key agreement protocol](https://popopx.chat/docs/glossary.md#key-agreement-protocol).

## Man-in-the-middle attack

An attack in which the adversary sits between two parties, relaying their traffic while each believes it is connected directly to the other, so messages can be read, altered or replaced and the encryption itself can be subverted during the initial key exchange.

The defence is to establish or verify keys outside the channel under attack: checking a fingerprint over a second channel, or receiving the key through a route the attacker does not control. POPOPX connections begin with an invitation link or QR code that already carries the keys, and clients verify the server fingerprint and use channel binding, which also prevents replay attacks.

## MITM attack

See [Man-in-the-middle attack](https://popopx.chat/docs/glossary.md#man-in-the-middle-attack).

## Merkle directed acyclic graph

A directed acyclic graph in which each node is identified by a hash of its contents together with the hashes of the nodes it points to, so any edit changes that identity and everything above it. Version control systems and content-addressed storage are built on it.

A [blockchain](https://popopx.chat/docs/glossary.md#blockchain) is the case where the graph never branches.

## Message padding

Adding data to a message so that its size on the wire carries less information about its content, and messages of different lengths become the same size. Padding one layer is not enough: if the content is padded but the packet carrying it is not, the outer length still gives a clue.

POPOPX pads at each encryption layer, so the sizes an SMP server or a network observer sees do not correspond to the size of the original content.

## Non-repudiation

The ability to prove afterwards that a particular person authored or sent something, typically with a signature made with a long-term key, so they cannot credibly deny it. It is what makes a signed document binding, and what turns a message log into evidence.

It is the opposite of [repudiation](https://popopx.chat/docs/glossary.md#repudiation), and for a private messenger it is a liability: a signature that binds messages to a persistent identity also binds that person to the connection graph.

## Onion routing

A method of hiding a connection's origin and destination by wrapping the traffic in several layers of encryption, each removed by one relay, so no single relay knows both ends of the circuit. Tor is the main implementation; its last relay still sees the payload, which is why application-level encryption is still required.

Onion routing hides network addresses, not message content. POPOPX does not build its own onion; you can instead carry the connection to its servers through Tor, so the server sees an overlay address rather than yours.

## Overlay network

A virtual network whose participants address one another through names and routes that are layered on an underlying network and invisible to it. Distributed hash tables, content networks and anonymity networks are all overlays on the public internet.

The sense this site uses is a transport overlay: instead of opening a direct connection to an SMP server, a POPOPX client can carry its traffic through Tor or a comparable overlay, which keeps the user's IP address from the server.

## Pairwise pseudonymous identifier

An identifier that holds for exactly one relationship, so the same participant is known by a different value to every peer, group or service, and an observer cannot join two relationships to the same entity.

POPOPX uses pairwise identifiers for its message queues: each contact and each group member has its own send and receive queue identifiers, none of them shared with another connection and none of them naming a user.

## Peer-to-peer

A network in which the participants communicate and store with one another directly rather than through a permanent server, so routing, availability and durability are distributed among them and there is no operator to censor or subpoena.

The costs are operational: routing usually depends on a variant of a distributed hash table, which trades delivery guarantee against latency; discoverable nodes invite Sybil and traffic-amplification attacks; and providers can block the traffic. POPOPX is not peer-to-peer: each message is written to a queue on the servers the recipient chose and collected when that device is online, so the peers need neither to meet nor to know each other's addresses.

## Perfect forward secrecy

See [Forward secrecy](https://popopx.chat/docs/glossary.md#forward-secrecy).

## Post-compromise security

The property that a session repairs itself: after an attacker who briefly held the current keys loses access, the keys are ratcheted forward, so messages sent from that point can no longer be decrypted with the stolen material. It is also called break-in recovery.

It is the counterpart of [forward secrecy](https://popopx.chat/docs/glossary.md#forward-secrecy), which protects the earlier messages, and both come from the same continuous key updates in the [double ratchet algorithm](https://popopx.chat/docs/glossary.md#double-ratchet-algorithm).

## Post-quantum cryptography

Algorithms designed to resist an attacker with a large quantum computer. The exposure is mainly in key agreement and signatures: the elliptic-curve and RSA constructions used today fall to Shor's algorithm, while lattice-based, code-based and hash-based schemes are not known to.

Because the newer schemes have had less scrutiny, deployments normally combine one with a classical exchange to form a hybrid key, which an attacker must break twice. POPOPX combines a post-quantum key encapsulation with X25519 on every ratchet step of its [double ratchet algorithm](https://popopx.chat/docs/glossary.md#double-ratchet-algorithm).

## Post-quantum hybrid crypto

See [Post-quantum cryptography](https://popopx.chat/docs/glossary.md#post-quantum-cryptography).

## Proxied peer-to-peer

A peer-to-peer design in which the peers cannot address each other directly, usually because of network address translation or firewalls, and so establish and carry their session through an intermediary that both can reach. The intermediary forwards a live session; the peers remain its endpoints.

That differs from the store-and-forward of POPOPX, where a server holds each message until the recipient retrieves it, so no session between the two devices has to exist at any moment.

## Recovery from compromise

See [Post-compromise security](https://popopx.chat/docs/glossary.md#post-compromise-security).

## Repudiation

The property that a participant can credibly deny having sent a message, because nothing the cryptography produced persuades a third party. It is destroyed by signatures over message content with a long-term key, and it is the opposite of [non-repudiation](https://popopx.chat/docs/glossary.md#non-repudiation); deniable authentication is why private messengers avoid both.

The comparison on this site credits POPOPX with repudiation, with the stated caveat that it covers the sender-to-recipient layer and not the client-server connection.

## User identity

A stable handle by which a network refers to a person - a phone number, an email address, a username or a public key. It is what allows anyone to find you, and it is also what lets an operator, or anyone who obtains its records, assemble your social graph.

POPOPX assigns no user identifiers of any kind: no phone number, username, account ID or random number. Profiles, contacts and groups exist only on the user's device, and the only addresses the network sees are the per-connection queue identifiers described as [pairwise pseudonymous identifiers](https://popopx.chat/docs/glossary.md#pairwise-pseudonymous-identifier).
