class BoostyMilker < Formula
  include Language::Python::Virtualenv

  desc "CLI tool to download photos from Boosty"
  homepage "https://github.com/F3T1W/BoostyMilker"
  url "https://github.com/F3T1W/BoostyMilker/archive/refs/tags/v1.0.3.tar.gz"
  sha256 "ee3fed85b56fecd1824ef9d26523ea5c2eb5d91648d31ae5c31835e3d355cfc3"
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/boosty-milker", "--help"
  end
end
