RANDOM = ARGV[0] ? Random.new(ARGV[0].to_i) : Random.new

EVENTS = %w[A B C D E F G H I J K L M N O P]
matched_user_ids = 3.times.map { RANDOM.rand(99999) }
unmatched_user_ids = 17.times.map{ RANDOM.rand(99999) }
interval = 1 # seconds over which to generate log data
start_time = Time.now.to_f
num_streams = 4

MATCH = %w[A B C]

num_triples_per_user = 20

def gen_triple
  triple = nil
  while !triple
    triple = 3.times.map do |n|
      EVENTS[RANDOM.rand(EVENTS.length)]
    end
  end
  triple
end

unmatched_user_seq = unmatched_user_ids.map do |id|
  seq = num_triples_per_user.times.map do
    gen_triple
  end.flatten
  # make sure there arent ANY matches in this data
  indices_to_change = seq.each_with_index.each_cons(3).select do |a|
    a.map(&:first) == MATCH
  end.map { |a| a.first.last }
  indices_to_change.each do |i|
    seq[i] = 'D'
  end
  seq.map { |a| [id, a] }
end
matched_user_seq = matched_user_ids.map do |id|
  match_index = RANDOM.rand(num_triples_per_user)
  num_triples_per_user.times.map do |n|
    n == match_index ? MATCH : gen_triple
  end.flatten.map { |a| [id, a] }
end

seqs = (unmatched_user_seq + matched_user_seq)

aggregated = []
unnormalized_time_offset = 0
until seqs.empty?
  seq = seqs[RANDOM.rand(seqs.length)]
  user_id_event = seq.shift
  unnormalized_time_offset += RANDOM.rand(200)
  aggregated << ([unnormalized_time_offset] + user_id_event)
  seqs.delete(seq) if seq.empty?
end

max_uto = aggregated.map {|a,b,c| a}.max

aggregated.map! do |a,b,c|
  [(a.to_f / max_uto * interval + start_time).to_f, b, c]
end

logfiles = num_streams.times.map { |n| File.open("log-#{n}.log", 'a') }

aggregated.each do |entry|
  timestamp = entry.first
  sleep([0, timestamp - Time.now.to_f].max)
  log_id = RANDOM.rand(num_streams)
  logfiles[log_id].puts(entry.join('|'))
  logfiles[log_id].flush
end

logfiles.each(&:close)

puts "expected user_ids: #{matched_user_ids}"
