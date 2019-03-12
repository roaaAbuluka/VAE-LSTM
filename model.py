import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


# TODO: don't forget to truncate eos when feeding to decoder
class VAELSTM(nn.Module):
    def __init__(self, encoder, decoder, latent_dim=1100):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        # TODO: activation?
        self.mu_linear = nn.Linear(hidden_size, latent_dim)
        self.sig_linear = nn.Linear(hiddne_size, latent_dim)

    def _reparameterize(self, mu, sig):
        z = torch.rand_like(mu) * sig + mu
        return z.unsqueeze(1) # (B, 1, 1100)

    def forward(self, orig, para):
        h_t = self.encoder(orig, para)
        mu = self.mu_linear(h_t)
        sig = self.sig_linear(h_t)
        z = self._reparameterize(mu, sig)
        logits = self.decoder(orig, para, z)
        return logits, mu, sig # (B, L, vocab_size), (B, 1100), (B, 1100)


class Encoder(nn.Module):
    def __init__(self):
        super().__init__(vocab_size, hidden_dim=600)
        self.embedding = nn.Embedding(vocab_size, 300)
        self.lstm_orig = nn.LSTM(300, hidden_dim, batch_first=True)
        self.lstm_para = nn.LSTM(300, hidden_dim, batch_first=True)

    def forward(self, orig, para):
        orig, orig_lengths = orig # (B, l), (B,)
        para, para_lengths = para
        orig = self.embedding(orig) # (B, l, 300)
        para = self.embedding(para)
        orig_packed = pack_padded_sequence(orig, orig_lengths,
                                           batch_first=true)
        para_packed = pack_padded_sequence(para, para_lengths,
                                           batch_first=True)
        # TODO: try parallel encoding w/o dependencies
        _, orig_hidden = self.lstm_orig(orig_packed)
        _, para_hidden = self.lstm_para(para_packed, orig_hidden)
        h_t, _ = para_hidden
        return h_t.squeeze(1) # (B, 600)


class Decoder(nn.Module):
    def __init__(self, vocab_size, hidden_dim=600, latent_dim=1100):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, 300)
        self.lstm_orig = nn.LSTM(300, hidden_dim, batch_first=True,
                                 num_layers=2)
        self.lstm_para = nn.LSTM(300 + latent_dim, hidden_dim,
                                 batch_first=True, num_layers=2)
        self.linear = nn.Linear(hidden_dim, vocab_size)

    def forward(self, orig, para, z):
        orig, orig_lengths = orig # (B, l), (B,)
        para, para_lengths = para
        orig = self.embedding(orig) # (B, l, 300)
        para = self.embedding(para)
        L = para.size(1)
        para_z = torch.cat([para, z.repeat(1, L, 1)], dim=-1) # (B, L, 1100+300)
        # z (B, 1, 1100)
        orig_packed = pack_padded_sequence(orig, orig_lengths,
                                           batch_first=true)
        para_z_packed = packed_padded_sequence(para_z, para_lengths,
                                               batch_first=true)
        _, orig_hidden = self.lstm_orig(orig_packed)
        # (B, L, 600)
        para_output, _ = self.lstm_para(para_packed, orig_hidden)
        logits = self.linear(para_output)
        return logits # (B, L, vocab_size)


def build_VAE(vocab_size, hidden_dim, latent_dim, share_emb=False,
              share_orig_enc=False, device=None):
    encoder = Encoder(vocab_size, hidden_dim)
    decoder = Decoder(vocab_size, hidden_dim, latent_dim)
    if share_emb:
        decoder.embedding.weight = encoder.embedding.weight
    vae = VAE(encoder, decoder, latent_dim)
    return vae.to(device)

