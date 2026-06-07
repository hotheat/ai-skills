#!/usr/bin/env ruby
# frozen_string_literal: true

require 'yaml'
require 'fileutils'

if ARGV.empty?
  warn 'usage: add_rules.rb DOMAIN-SUFFIX,example.com,Proxy [DOMAIN,foo.example,Proxy ...]'
  exit 2
end

BASE = File.expand_path('~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev')
TARGETS = [
  File.expand_path('~/.clash-verge/my-local.yaml'),
  File.join(BASE, 'profiles', 'Lj28jGfzuySk.yaml'),
  File.join(BASE, 'clash-verge.yaml'),
  File.join(BASE, 'clash-verge-check.yaml')
].freeze
PROFILES_META = File.join(BASE, 'profiles.yaml')

new_rules = ARGV.map(&:strip).reject(&:empty?).uniq
invalid = new_rules.reject { |rule| rule.count(',') >= 2 }
unless invalid.empty?
  warn "invalid rule(s): #{invalid.join(' ')}"
  exit 2
end

def merge_rules(config, new_rules)
  rules = config.fetch('rules')
  rules = rules.reject { |rule| new_rules.include?(rule) }
  first_direct = rules.index do |rule|
    rule.end_with?(',DIRECT') || rule.start_with?('GEOIP,') || rule.start_with?('IP-CIDR')
  end || rules.length
  rules.insert(first_direct, *new_rules)
  rules.map! { |rule| ['MATCH,Proxy', 'MATCH,Bitz Net'].include?(rule) ? 'MATCH,DIRECT' : rule }
  config['rules'] = rules
  config
end

timestamp = Time.now.strftime('%Y%m%d%H%M%S')

TARGETS.each do |path|
  raise "missing file: #{path}" unless File.exist?(path)

  FileUtils.cp(path, "#{path}.bak-#{timestamp}")
  config = YAML.load_file(path)
  config = merge_rules(config, new_rules)
  File.write(path, YAML.dump(config))
  puts "updated #{path} rules=#{config.fetch('rules').length}"
end

raise "missing file: #{PROFILES_META}" unless File.exist?(PROFILES_META)

FileUtils.cp(PROFILES_META, "#{PROFILES_META}.bak-#{timestamp}")
meta = YAML.load_file(PROFILES_META)
meta['current'] = 'Lj28jGfzuySk'
File.write(PROFILES_META, YAML.dump(meta))
puts 'current=Lj28jGfzuySk'
