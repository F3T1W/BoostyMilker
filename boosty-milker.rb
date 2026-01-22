class BoostyMilker < Formula
  include Language::Python::Virtualenv

  desc "CLI tool to download photos from Boosty"
  homepage "https://github.com/F3T1W/BoostyMilker"
  url "https://github.com/F3T1W/BoostyMilker/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_SHA256"
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/boosty-milker", "--help"
  end
end
