data {
  int<lower=0> n;
  int<lower=0> m;
  int uns_zeros[3,n];
  vector[m] musicas;
}
parameters {  
  simplex[3] playlist_theta;
  real<lower=0> playlist_alpha;
  real<lower=0> playlist_beta;
}
model {
  for (i in 1:n)
    uns_zeros[,i] ~ multinomial(playlist_theta);

  musicas ~ beta(playlist_alpha, playlist_beta);
}
