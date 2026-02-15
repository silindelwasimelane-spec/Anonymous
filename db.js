const path = require('path');
const fs = require('fs');

const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });

const storePath = path.join(dataDir, 'store.json');

function readStore() {
  try {
    const raw = fs.readFileSync(storePath, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    return { nextMsgId: 1, messages: [], nextUserId: 1, users: [], tokens: {} };
  }
}

function writeStore(store) {
  const tmp = storePath + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(store));
  fs.renameSync(tmp, storePath);
}

function addMessageToUserByUserId(userId, content) {
  const store = readStore();
  const id = store.nextMsgId++;
  const msg = { id, content, created_at: Date.now(), userId };
  store.messages.unshift(msg);
  if (store.messages.length > 10000) store.messages.length = 10000;
  writeStore(store);
  return id;
}

function addMessageToUserByRecipient(recipientId, content) {
  const store = readStore();
  const user = store.users.find(u => u.recipientId === recipientId);
  if (!user) return null;
  return addMessageToUserByUserId(user.id, content);
}

function getMessagesForUserId(userId, limit = 100) {
  const store = readStore();
  return store.messages.filter(m => m.userId === userId).slice(0, limit);
}

function createUser(username, passwordHash, recipientId) {
  const store = readStore();
  const id = store.nextUserId++;
  const user = { id, username, passwordHash, recipientId };
  store.users.push(user);
  writeStore(store);
  return user;
}

function getUserByUsername(username) {
  const store = readStore();
  return store.users.find(u => u.username === username) || null;
}

function getUserById(id) {
  const store = readStore();
  return store.users.find(u => u.id === id) || null;
}

function getUserByRecipientId(recipientId) {
  const store = readStore();
  return store.users.find(u => u.recipientId === recipientId) || null;
}

module.exports = {
  addMessageToUserByRecipient,
  addMessageToUserByUserId,
  getMessagesForUserId,
  createUser,
  getUserByUsername,
  getUserById,
  getUserByRecipientId,
};
